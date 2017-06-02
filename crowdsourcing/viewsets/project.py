import json
from decimal import Decimal, ROUND_UP
from itertools import groupby
from textwrap import dedent

import numpy as np
from django.conf import settings
from django.db import connection
from django.db.models import F
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from yapf.yapflib.yapf_api import FormatCode

from crowdsourcing.discourse import DiscourseClient
from crowdsourcing.models import Category, Project, Task, TaskWorker
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator, ProjectChangesAllowed
from crowdsourcing.serializers.project import *
from crowdsourcing.serializers.task import *
from crowdsourcing.tasks import create_tasks_for_project
from crowdsourcing.utils import get_pk, get_template_tokens, SmallResultsSetPagination
from crowdsourcing.validators.project import validate_account_balance
from mturk.tasks import mturk_disable_hit


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.active()
    serializer_class = ProjectSerializer
    pagination_class = SmallResultsSetPagination
    permission_classes = [IsProjectOwnerOrCollaborator, IsAuthenticated, ProjectChangesAllowed]

    def create(self, request, with_defaults=True, *args, **kwargs):
        serializer = ProjectSerializer(
            data=request.data,
            fields=('name', 'price', 'post_mturk', 'repetition', 'template'),
            context={'request': request}
        )

        if serializer.is_valid():
            with transaction.atomic():
                project = serializer.create(owner=request.user, with_defaults=with_defaults)

                serializer = ProjectSerializer(
                    instance=project,
                    fields=('id', 'name'),
                    context={'request': request}
                )

                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['post'], url_path='create-full')
    def create_full(self, request, *args, **kwargs):
        price = request.data.get('price')
        post_mturk = request.data.get('post_mturk', False)
        repetition = request.data.get('repetition', 1)
        if not post_mturk:
            validate_account_balance(request, int(price * 100) * repetition)
        return self.create(request=request, with_defaults=False, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        serializer = ProjectSerializer(instance=self.get_object(),
                                       fields=('id', 'name', 'price', 'repetition', 'deadline', 'timeout',
                                               'is_prototype', 'template', 'status', 'post_mturk',
                                               'qualification', 'group_id', 'revisions', 'task_time',
                                               'has_review', 'parent', 'hash_id', 'is_api_only', 'batch_files'),
                                       context={'request': request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectSerializer(
            instance=instance, data=request.data, partial=True, context={'request': request}
        )

        if serializer.is_valid():
            with transaction.atomic():
                serializer.update()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == Project.STATUS_DRAFT:
            instance.hard_delete()
        else:
            mturk_disable_hit.delay({'id': instance.group_id})
            Project.objects.filter(
                Q(parent_id=instance.group_id, is_review=True) | Q(group_id=instance.group_id)).update(
                deleted_at=timezone.now())

        return Response(data={}, status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['PUT'])
    def update_status(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance, data=request.data)
        serializer.update_status()
        return Response({}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='payment')
    def payment(self, request, *args, **kwargs):
        instance = self.get_object()
        total_needed = self._calculate_total(instance)
        to_pay = (Decimal(total_needed) - instance.amount_due).quantize(Decimal('.01'), rounding=ROUND_UP)
        return Response({"to_pay": to_pay, "total": total_needed})

    @detail_route(methods=['get'], url_path='submitted-tasks-count')
    def submitted_tasks_count(self, request, *args, **kwargs):
        instance = self.get_object()
        task_worker_count = TaskWorker.objects.filter(task__project__group_id=instance.group_id,
                                                      status=TaskWorker.STATUS_SUBMITTED).count()
        return Response({"submitted": task_worker_count})

    @staticmethod
    def _calculate_total(instance):
        cursor = connection.cursor()
        # noinspection SqlResolve
        payment_query = '''
            WITH RECURSIVE cte(id, group_id, project_id, price, exclude_at, level) AS (
              SELECT
                t.id,
                t.group_id,
                project_id,
                p.price,
                exclude_at,
                1 AS level
              FROM crowdsourcing_task t
                INNER JOIN crowdsourcing_project p ON p.id = t.project_id
              WHERE project_id = (%(current_pid)s)
              UNION ALL
              SELECT
                t.id,
                t.group_id,
                t.project_id,
                p.price,
                t.exclude_at,
                c.level + 1 AS level
              FROM crowdsourcing_task t
                INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                INNER JOIN cte c
                  ON t.id = c.id
              WHERE c.level < p.repetition AND t.project_id = (%(current_pid)s)
            )
            SELECT sum(to_pay) AS total_needed
            FROM (
                   SELECT
                     cte.id       task_id,
                     cte.group_id group_id,
                     cte.price    new_price,
                     prev.id      prev_task_id,
                     prev.price   old_price,
                     prev.status,
                     prev.exclude_at,
                     CASE WHEN prev.status = 3 AND (cte.id IS NULL OR (cte.id IS NOT NULL AND prev.exclude_at IS NULL))
                       THEN 0
                     WHEN prev.status <> 3 AND cte.id IS NULL
                       THEN
                         prev.price
                     WHEN prev.id IS NULL OR (cte.id IS NOT NULL AND prev.exclude_at IS NOT NULL AND prev.status = 3)
                       THEN
                         cte.price
                     WHEN prev.id IS NOT NULL AND cte.id IS NOT NULL AND prev.exclude_at IS NULL AND prev.status <> 3
                       THEN greatest(prev.price, cte.price)
                     WHEN prev.id IS NOT NULL AND cte.id IS NOT NULL
                        AND prev.exclude_at IS NOT NULL AND prev.status <> 3
                       THEN
                         greatest(COALESCE(cte.price, 0), COALESCE(prev.price, 0))
                     END          to_pay
                   FROM cte
                     FULL OUTER JOIN (
                                       SELECT
                                         t.id,
                                         t.group_id,
                                         p.price,
                                         p.id                      project_id,
                                         tw.status,
                                         tw.worker_id,
                                         t.exclude_at,
                                         row_number()
                                         OVER (PARTITION BY t.group_id
                                           ORDER BY t.group_id) AS level
                                       FROM crowdsourcing_taskworker tw
                                         INNER JOIN crowdsourcing_task t ON t.id = tw.task_id
                                         INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                                       WHERE tw.status NOT IN (4, 6, 7) and p.group_id = (%(project_group_id)s)
                                     ) prev
                       ON cte.group_id = prev.group_id AND cte.level = prev.level AND
                          coalesce(prev.exclude_at, cte.project_id) = cte.project_id
                   ORDER BY cte.group_id, cte.level) w;
                '''
        cursor.execute(payment_query, {'current_pid': instance.id, "project_group_id": instance.group_id})
        total_needed = cursor.fetchall()[0][0]
        return total_needed

    @detail_route(methods=['POST'])
    def publish(self, request, pk=None, *args, **kwargs):
        num_rows = request.data.get('num_rows', 0)
        project_id, is_hash = get_pk(pk)
        filter_by = {}
        if is_hash:
            filter_by.update({'group_id': project_id})
        else:
            filter_by.update({'pk': project_id})
        instance = self.queryset.filter(**filter_by).order_by('-id').first()
        with transaction.atomic():
            if num_rows > 0:
                instance.tasks.filter(row_number__gt=num_rows).delete()

            data = copy.copy(request.data)
            data["status"] = Project.STATUS_IN_PROGRESS

            serializer = ProjectSerializer(
                instance=instance, data=data, partial=True, context={'request': request}
            )
            relaunch = serializer.get_relaunch(instance)
            if relaunch['is_forced'] or (not relaunch['is_forced'] and not relaunch['ask_for_relaunch']):
                tasks = models.Task.objects.active().filter(~Q(project_id=instance.id),
                                                            project__group_id=instance.group_id)
                task_serializer = TaskSerializer()
                task_serializer.bulk_update(tasks, {'exclude_at': instance.id})

        total_needed = self._calculate_total(instance)
        to_pay = (Decimal(total_needed) - instance.amount_due).quantize(Decimal('.01'), rounding=ROUND_UP)
        instance.amount_due = total_needed if total_needed is not None else 0
        if not instance.post_mturk:
            validate_account_balance(request, int(to_pay * 100))

        if serializer.is_valid():
            with transaction.atomic():
                serializer.publish(to_pay)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['get'], url_path='for-workers')
    def worker_projects(self, request, *args, **kwargs):
        # noinspection SqlResolve
        query = '''
            SELECT
              id,
              name,
              owner_id,
              status,
              round(price, 2),
              sum(returned)         returned,
              sum(in_progress)      in_progress,
              sum(accepted)         completed,
              sum(submitted)         awaiting_review,
              case when min(estimated_expire) < now() then null else min(estimated_expire) end expires_at
            FROM (SELECT
                    p.group_id                                                                      id,
                    p.name,
                    p.owner_id,
                    p.status,
                    p.price,
                    coalesce(p.timeout, INTERVAL %(default_timeout)s) timeout,
                    coalesce(tw.started_at, tw.created_at) + coalesce(p.timeout,
                        INTERVAL %(default_timeout)s) estimated_expire,
                    CASE WHEN tw.status = (%(returned)s)
                      THEN 1
                    ELSE 0 END                                                                      returned,
                    CASE WHEN tw.status = (%(in_progress)s)
                      THEN 1
                    ELSE 0 END                                                                      in_progress,
                    CASE WHEN tw.status = %(accepted)s
                      THEN 1
                    ELSE 0 END                                                                      accepted,
                    CASE WHEN tw.status = %(submitted)s
                      THEN 1
                    ELSE 0 END                                                                       submitted
                  FROM crowdsourcing_taskworker tw
                    INNER JOIN crowdsourcing_task t ON tw.task_id = t.id
                    INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                  WHERE tw.status <> (%(skipped)s) AND tw.worker_id = (%(worker_id)s) AND p.is_review = FALSE) tw
            GROUP BY tw.id, tw.name, tw.owner_id, tw.status, tw.price
            ORDER BY returned DESC, in_progress DESC, id DESC;
        '''
        projects = Project.objects.raw(query, params={
            'worker_id': request.user.id,
            'skipped': TaskWorker.STATUS_SKIPPED,
            'in_progress': TaskWorker.STATUS_IN_PROGRESS,
            'returned': TaskWorker.STATUS_RETURNED,
            'accepted': TaskWorker.STATUS_ACCEPTED,
            'submitted': TaskWorker.STATUS_SUBMITTED,
            'default_timeout': '24 hour'
        })

        serializer = ProjectSerializer(instance=projects, many=True,
                                       fields=('id', 'name', 'owner', 'price', 'status', 'returned',
                                               'in_progress', 'awaiting_review', 'completed', 'expires_at'),
                                       context={'request': request})
        response_data = {
            "in_progress": [],
            "completed": [],
        }
        for p in serializer.data:
            if p['returned'] > 0 or p['in_progress'] > 0:
                response_data['in_progress'].append(p)
            elif p['completed'] > 0 or p['awaiting_review'] > 0:
                response_data['completed'].append(p)
        return Response(data=response_data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'], url_path='for-requesters')
    def requester_projects(self, request, *args, **kwargs):
        # noinspection SqlResolve
        query = '''
            SELECT
              id,
              group_id,
              name,
              created_at,
              updated_at,
              status,
              price,
              published_at,
              completed,
              awaiting_review,
              in_progress
            FROM crowdsourcing_project p
              INNER JOIN (
                           SELECT
                             p_max.id  project_id,
                             sum(completed) completed,
                             sum(awaiting_review) awaiting_review,
                             greatest((p0.repetition * count(DISTINCT task_id)) - sum(completed) -
                               sum(awaiting_review), 0) in_progress
                           FROM (
                                  SELECT
                                    p.group_id,
                                    t.group_id task_id,
                                    CASE WHEN tw.status = 3
                                      THEN 1
                                    ELSE 0 END completed,
                                    CASE WHEN tw.status = 2
                                      THEN 1
                                    ELSE 0 END awaiting_review
                                  FROM crowdsourcing_project p
                                    LEFT OUTER JOIN crowdsourcing_task t ON t.project_id = p.id
                                      AND t.deleted_at IS NULL
                                    LEFT OUTER JOIN crowdsourcing_taskworker tw ON tw.task_id = t.id
                                  WHERE p.owner_id = (%(owner_id)s) AND p.deleted_at IS NULL AND is_review = FALSE) c
                             INNER JOIN (SELECT
                                           group_id,
                                           max(id) id
                                         FROM crowdsourcing_project
                                         GROUP BY group_id) p_max
                               ON c.group_id = p_max.group_id
                             INNER JOIN crowdsourcing_project p0 ON p0.id=p_max.id
                           GROUP BY p_max.id, p0.repetition) t
                ON t.project_id = p.id
            ORDER BY updated_at DESC;
        '''
        projects = Project.objects.raw(query, params={'owner_id': request.user.id})
        serializer = ProjectSerializer(instance=projects, many=True,
                                       fields=('id', 'group_id', 'name', 'age', 'total_tasks', 'in_progress',
                                               'completed', 'awaiting_review', 'status', 'price', 'hash_id',
                                               'revisions', 'updated_at', 'discussion_link'),
                                       context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='status')
    def status(self, request, *args, **kwargs):
        # noinspection SqlResolve
        query = '''
            SELECT
              id,
              group_id,
              name,
              created_at,
              updated_at,
              status,
              price,
              published_at,
              completed,
              awaiting_review,
              in_progress
            FROM crowdsourcing_project p
              INNER JOIN (
                           SELECT
                             p_max.id  project_id,
                             sum(completed) completed,
                             sum(awaiting_review) awaiting_review,
                             greatest((p0.repetition * count(DISTINCT task_id)) - sum(completed) -
                               sum(awaiting_review), 0) in_progress
                           FROM (
                                  SELECT
                                    p.group_id,
                                    t.group_id task_id,
                                    CASE WHEN tw.status = 3
                                      THEN 1
                                    ELSE 0 END completed,
                                    CASE WHEN tw.status = 2
                                      THEN 1
                                    ELSE 0 END awaiting_review
                                  FROM crowdsourcing_project p
                                    LEFT OUTER JOIN crowdsourcing_task t ON t.project_id = p.id
                                      AND t.deleted_at IS NULL
                                    LEFT OUTER JOIN crowdsourcing_taskworker tw ON tw.task_id = t.id
                                  WHERE p.owner_id = (%(owner_id)s) AND p.deleted_at IS NULL AND is_review = FALSE) c
                             INNER JOIN (SELECT
                                           group_id,
                                           max(id) id
                                         FROM crowdsourcing_project
                                         GROUP BY group_id) p_max
                               ON c.group_id = p_max.group_id
                             INNER JOIN crowdsourcing_project p0 ON p0.id=p_max.id
                           GROUP BY p_max.id, p0.repetition) t
                ON t.project_id = p.id
            WHERE p.id = (%(pk)s)
        '''
        projects = Project.objects.raw(query, params={'owner_id': request.user.id, "pk": kwargs.get('pk')})
        serializer = ProjectSerializer(instance=projects, many=True,
                                       fields=('id', 'group_id', 'name', 'age', 'total_tasks', 'in_progress',
                                               'completed', 'awaiting_review', 'status', 'price', 'hash_id',
                                               'revisions', 'updated_at'),
                                       context={'request': request})
        return Response(serializer.data[0] if len(serializer.data) else {})

    @detail_route(methods=['post'])
    def fork(self, request, *args, **kwargs):
        instance = self.get_object()
        project_serializer = ProjectSerializer(instance=instance, data=request.data, partial=True,
                                               fields=('id', 'name', 'price', 'repetition',
                                                       'is_prototype', 'template', 'status', 'batch_files'))
        if project_serializer.is_valid():
            with transaction.atomic():
                project_serializer.fork()
            return Response(data=project_serializer.data, status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError(detail=project_serializer.errors)

    @detail_route(methods=['get'], permission_classes=[IsAuthenticated])
    def preview(self, request, *args, **kwargs):
        project = self.get_object()
        task = Task.objects.filter(project=project).first()
        task_serializer = TaskSerializer(instance=task, fields=('id', 'template'))
        return Response(data=task_serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['get'], url_path='task-feed')
    def task_feed(self, request, *args, **kwargs):
        projects = Project.objects.filter_by_boomerang(request.user)
        project_serializer = ProjectSerializer(instance=projects, many=True,
                                               fields=('id', 'name',
                                                       'timeout',
                                                       'available_tasks',
                                                       'price',
                                                       'task_time',
                                                       'discussion_link',
                                                       'requester_handle',
                                                       'requester_rating', 'raw_rating', 'is_prototype', 'is_review',),
                                               context={'request': request})

        return Response(data=project_serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def comments(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectCommentSerializer(instance=instance.comments, many=True, fields=('comment', 'id',))
        response_data = {
            'project': kwargs['pk'],
            'comments': serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='post-comment')
    def post_comment(self, request, *args, **kwargs):
        serializer = ProjectCommentSerializer(data=request.data)
        comment_data = {}
        if serializer.is_valid():
            comment = serializer.create(project=kwargs['pk'], sender=request.user)
            comment_data = ProjectCommentSerializer(
                comment,
                fields=('id', 'comment',),
                context={'request': request}).data

        return Response(data=comment_data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def attach_file(self, request, **kwargs):
        serializer = ProjectBatchFileSerializer(data=request.data, fields=('batch_file',))
        if serializer.is_valid():
            project_file = serializer.create(project=kwargs['pk'])
            file_serializer = ProjectBatchFileSerializer(instance=project_file)
            create_tasks_for_project.delay(kwargs['pk'], False)
            return Response(data=file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @detail_route(methods=['delete'])
    def delete_file(self, request, **kwargs):
        batch_file = request.data.get('batch_file', None)
        instances = models.ProjectBatchFile.objects.filter(batch_file=batch_file)
        if instances.count() == 1:
            models.BatchFile.objects.filter(id=batch_file).delete()
        else:
            models.ProjectBatchFile.objects.filter(batch_file_id=batch_file, project_id=kwargs['pk']).delete()
        create_tasks_for_project.delay(kwargs['pk'], True)
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='create-revision')
    def create_revision(self, request, *args, **kwargs):
        project = self.get_object()
        with transaction.atomic():
            revision = self.serializer_class.create_revision(instance=project)
        return Response(data={'id': revision.id}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='relaunch-info')
    def relaunch_info(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.serializer_class(instance=project, fields=('id', 'relaunch'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='add-data')
    def add_data(self, request, pk, *args, **kwargs):
        tasks = request.data.get('tasks', [])
        run_key = request.data.get('rerun_key', None)
        parent_batch_id = request.data.get('parent_batch_id', None)
        batch = models.Batch.objects.create(parent_id=parent_batch_id)
        project_id, is_hash = get_pk(pk)
        filter_by = {}
        if is_hash:
            filter_by.update({'group_id': project_id})
        else:
            filter_by.update({'pk': project_id})
        project = self.queryset.filter(**filter_by).order_by('-id').first()

        existing_tasks = Task.objects.filter(project=project, rerun_key=run_key, exclude_at__isnull=True)

        task_objects = []
        all_hashes = [hash_task(data=task) for task in tasks if task]
        # to_pay = Decimal(project.price * project.repetition * len(tasks)).quantize(Decimal('.01'), rounding=ROUND_UP)
        task_count = existing_tasks.count()
        existing_tasks.filter(hash__in=all_hashes).prefetch_related('task_workers')
        existing_hashes = existing_tasks.values_list('hash', flat=True)
        new_hashes = []

        row = 0
        response = {
            "project_key": pk,
            "tasks": []
        }

        for i, task in enumerate(tasks):
            if task:
                row += 1
                hash_digest = all_hashes[i]
                if hash_digest not in existing_hashes:
                    new_hashes.append(hash_digest)
                    price = None
                    if project.allow_price_per_task and project.task_price_field is not None:
                        price = row.get(project.task_price_field)
                    task_objects.append(
                        models.Task(project=project, data=task, hash=hash_digest, row_number=task_count + row,
                                    rerun_key=run_key, batch_id=batch.id, price=price))

        # TODO uncomment when we stop using MTurk: validate_account_balance(request, to_pay)
        task_serializer = TaskSerializer()

        for t in existing_tasks:
            if t.hash in all_hashes:
                task_workers = models.TaskWorker.objects.filter(task__group_id=t.group_id,
                                                                status__in=[models.TaskWorker.STATUS_ACCEPTED,
                                                                            models.TaskWorker.STATUS_SUBMITTED,
                                                                            models.TaskWorker.STATUS_REJECTED])
                response['tasks'].append({
                    "id": t.id,
                    "group_id": t.group_id,
                    "task_group_id": t.group_id,
                    "data": t.data,
                    "expected": max(task_workers.exclude(status=models.TaskWorker.STATUS_REJECTED).count(),
                                    project.repetition),
                    "task_workers": TaskWorkerSerializer(
                        task_workers,
                        many=True,
                        fields=(
                            'id', 'task_group_id', 'worker', 'status', 'created_at',
                            'updated_at', 'task',
                            'worker_alias', 'results', 'project_data',
                            'task_data')).data
                })

        with transaction.atomic():
            task_serializer.bulk_create(task_objects)
            task_objects = task_serializer.bulk_update(
                models.Task.objects.filter(project=project, rerun_key=run_key, hash__in=new_hashes),
                {'group_id': F('id')})

            for t in task_objects:
                response['tasks'].append({
                    "id": t.id,
                    "group_id": t.group_id,
                    "task_group_id": t.group_id,
                    "data": t.data,
                    "expected": project.repetition,
                    "task_workers": []
                })

            if project.status != Project.STATUS_DRAFT:
                project_serializer = ProjectSerializer(instance=project)
                # project_serializer.pay(to_pay)
                project_serializer.reset_boomerang()
                # project.amount_due += to_pay
                # project.save()

        # serializer = TaskSerializer(instance=task_objects, many=True)
        return Response(data=response, status=status.HTTP_201_CREATED)

    @detail_route(methods=['get'], url_path='is-done')
    def is_done(self, request, pk=None, *args, **kwargs):
        project_id, is_hash = get_pk(pk)
        project = None
        if not is_hash:
            project = self.get_object()
        else:
            project = Project.objects.filter(group_id=project_id).order_by('-id').first()
        batch_id = request.query_params.get('batch_id', -1)
        if project.deadline is not None and timezone.now() > project.deadline:
            return Response(data={"is_done": True}, status=status.HTTP_200_OK)
        extra_query = ' AND batch_id=(%(batch_id)s) '
        if batch_id < 0:
            extra_query = ''
        # noinspection SqlResolve
        query = '''
            SELECT
              count(t.id) remaining

            FROM crowdsourcing_task t INNER JOIN (SELECT
                                                    group_id,
                                                    max(id) id
                                                  FROM crowdsourcing_task
                                                  WHERE deleted_at IS NULL
            '''
        query += extra_query

        query += '''
                                                  GROUP BY group_id) t_max ON t_max.id = t.id
              INNER JOIN crowdsourcing_project p ON p.id = t.project_id
              INNER JOIN (
                           SELECT
                             t.group_id,
                             sum(t.others) OTHERS
                           FROM (
                                  SELECT
                                    t.group_id,
                                    CASE WHEN tw.id IS NOT NULL THEN 1 ELSE 0 END OTHERS
                                  FROM crowdsourcing_task t
                                    LEFT OUTER JOIN crowdsourcing_taskworker tw
                                    ON (t.id = tw.task_id AND tw.status NOT IN (4, 6, 7))
                                  WHERE t.exclude_at IS NULL AND t.deleted_at IS NULL) t
                           GROUP BY t.group_id) t_count ON t_count.group_id = t.group_id
            WHERE t_count.others < p.repetition AND p.id=(%(project_id)s)
            GROUP BY p.id;
        '''

        cursor = connection.cursor()
        cursor.execute(query, {'project_id': project.id, 'batch_id': batch_id})
        remaining_count = cursor.fetchall()[0][0] if cursor.rowcount > 0 else 0
        return Response(data={"is_done": remaining_count == 0}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='sample-script')
    def sample_script(self, request, *args, **kwargs):
        project = self.get_object()

        template_items = project.template.items.all()

        tokens = []
        output = {}
        for item in template_items:
            aux_attrib = item.aux_attributes
            if 'src' in aux_attrib:
                tokens += get_template_tokens(aux_attrib['src'])
            if 'question' in aux_attrib:
                tokens += get_template_tokens(aux_attrib['question']['value'])
            if 'options' in aux_attrib:
                for option in aux_attrib['options']:
                    tokens += get_template_tokens(option['value'])

            if item.role == models.TemplateItem.ROLE_INPUT:
                output["'%s'" % item.name] = "response.get('fields').get('%s')" % item.name

        data = {}
        input = {}
        for token in tokens:
            data[token] = "value"
            input["'%s'" % token] = "response.get('task_data').get('%s')" % token

        hash_id = ProjectSerializer.get_hash_id(project)

        task_data = json.dumps([data], indent=4, separators=(',', ': '))
        task_input = json.dumps(input, indent=4, separators=(',', ': ')).replace('\"', '')
        task_output = json.dumps(output, indent=4, separators=(',', ': ')).replace('\"', '')

        sandbox = ""
        sandbox_import = ""
        if settings.IS_SANDBOX:
            sandbox = ", host=SANDBOX"
            sandbox_import = "from daemo.constants import SANDBOX"

        script = \
            """
            %s
            from daemo.client import DaemoClient

            # Remember any task launched under this rerun key, so you can debug or resume the by re-running
            RERUN_KEY = 'myfirstrun'
            # The key for your project, copy-pasted from the project editing page
            PROJECT_KEY='%s'

            # If your project has inputs, send them as dicts
            # to the publish() call. Daemo will publish a
            # task for each item in the list
            task_data = %s

            # Create the client
            client = DaemoClient(rerun_key=RERUN_KEY%s)

            def approve(worker_responses):
                \"\"\"
                The approve callback is called when work is complete; it receives
                a list of worker responses. Return a list of True (approve) and
                False (reject) values. Approved tasks are passed on to the
                completed callback, and	rejected tasks are automatically relaunched.
                \"\"\"

                approvals = [True] * len(worker_responses)
                for count, response in enumerate(worker_responses):
                    task_input = %s

                    task_output = %s

                    # TODO write your approve function here
                    # approvals[count] = True or False

                return approvals


            def completed(worker_responses):
                \"\"\"
                Once tasks are approved, the completed callback is sent a list of
                final approved worker responses. Perform any computation that you
                want on the results. Don't forget to send Daemo the	rating scores
                so that it can improve and find better workers next time.
                \"\"\"

                # TODO write your completed function here
                # ratings = [{
                #    \"task_id\": response.get(\"task_id\"),
                #    \"worker_id\": response.get(\"worker_id\"),
                #    \"weight\": <<WRITE RATING FUNCTION HERE>> }
                #   for response in worker_responses]

                client.rate(project_key=PROJECT_KEY, ratings=ratings)

            # Publish the tasks
            client.publish(
                project_key=PROJECT_KEY,
                tasks=task_data,
                approve=approve,
                completed=completed
            )
            """

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="daemo_script.py"'
        final_script = dedent(script) % (sandbox_import, hash_id, task_data, sandbox, task_input, task_output)
        response.content, _ = FormatCode(final_script, verify=False)
        return response

    @detail_route(methods=['get'], url_path="review-submissions")
    def review_submissions(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        prefetch = ('worker', 'task', 'task__project', 'task__project__template')
        task_workers = TaskWorker.objects.prefetch_related(*prefetch).filter(status__in=[2, 3, 5],
                                                                             task__project__group_id=obj.group_id
                                                                             ).order_by('-id')[:64]

        serializer = TaskWorkerSerializer(instance=task_workers, many=True,
                                          fields=('id', 'results', 'worker', 'status', 'task',
                                                  'task_template', 'worker_alias', 'worker_rating',))
        group_by_worker = []
        for key, group in groupby(sorted(serializer.data), lambda x: x['worker_alias']):
            tasks = []
            worker_ratings = []
            for g in group:
                del g['worker_alias']
                tasks.append(g)
                if g['worker_rating']['weight'] is not None:
                    worker_ratings.append(g['worker_rating']['weight'])
                del g['worker_rating']
            group_by_worker.append(
                {"worker_alias": key, "worker": tasks[0]['worker'],
                 "worker_rating": {"weight": np.mean(worker_ratings) if len(worker_ratings) else None,
                                   'origin_type': models.Rating.RATING_REQUESTER},
                 "tasks": tasks})
        return Response(data={"workers": group_by_worker}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path="rate-submissions")
    def rate_submissions(self, request, pk, *args, **kwargs):
        obj = self.get_object()

        up_to = request.query_params.get('up_to')
        if up_to is None:
            up_to = timezone.now()
        task_workers = TaskWorker.objects.prefetch_related('worker', 'task', 'task__project', 'worker__profile') \
            .filter(
            status__in=[2, 3, 5],
            submitted_at__lte=up_to,
            task__project_id=obj.id).order_by('worker_id', '-id')
        task_workers = self.paginate_queryset(task_workers)

        serializer = TaskWorkerSerializer(instance=task_workers, many=True,
                                          fields=('id', 'results', 'worker', 'status', 'task',
                                                  'task_template', 'worker_alias', 'worker_rating',
                                                  'submitted_at', 'approved_at'))
        group_by_worker = []
        response = self.get_paginated_response(serializer.data)
        for key, group in groupby(sorted(response.data['results']), lambda x: x['worker_alias']):
            tasks = []
            worker_ratings = []
            for g in group:
                del g['worker_alias']
                tasks.append(g)
                if g['worker_rating']['weight'] is not None:
                    worker_ratings.append(g['worker_rating']['weight'])
                del g['worker_rating']
            group_by_worker.append(
                {"worker_alias": key, "worker": tasks[0]['worker'],
                 "worker_rating": {"weight": np.mean(worker_ratings) if len(worker_ratings) else None,
                                   'origin_type': models.Rating.RATING_REQUESTER},
                 "tasks": tasks})
        # group_by_worker.sort(key=lambda x: x['tasks'].count, reverse=True)
        return Response(
            data={"workers": group_by_worker, "count": response.data['count'], "next": response.data['next'],
                  "up_to": up_to},
            status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='last-opened')
    def last_opened(self, request, *args, **kwargs):
        project = self.get_object()
        last_opened_at = copy.copy(project.last_opened_at)
        project.last_opened_at = timezone.now()
        project.save()
        return Response({"last_opened_at": last_opened_at, "id": project.id})

    @detail_route(methods=['get'], url_path='worker-statistics')
    def worker_statistics(self, request, *args, **kwargs):
        project = self.get_object()
        worker_ids = TaskWorker.objects.prefetch_related('worker__profile').filter(
            task__project_id=project.id,
            status__in=[TaskWorker.STATUS_SUBMITTED, TaskWorker.STATUS_ACCEPTED,
                        TaskWorker.STATUS_RETURNED]).values_list('worker_id', flat=True)
        profiles = models.UserProfile.objects.prefetch_related('address__city').filter(user_id__in=worker_ids)
        response_data = {
            "education": {
                "unspecified": 0
            },
            "gender": {
                "unspecified": 0
            },
            "ethnicity": {
                "unspecified": 0
            },
            "age": {
                "unspecified": 0
            },
            "location": {
                "unspecified": 0
            }
        }
        if len(profiles) >= 10:
            for p in profiles:
                if p.education is None:
                    response_data["education"]["unspecified"] += 1
                else:
                    if p.education not in response_data["education"]:
                        response_data["education"][p.education] = 0
                    response_data["education"][p.education] += 1

                if p.ethnicity is None:
                    response_data["ethnicity"]["unspecified"] += 1
                else:
                    if p.ethnicity not in response_data["ethnicity"]:
                        response_data["ethnicity"][p.ethnicity] = 0
                    response_data["ethnicity"][p.ethnicity] += 1

                if p.address is None:
                    response_data["location"]["unspecified"] += 1
                else:
                    pass
                    # if p.ethnicity not in response_data["ethnicity"]:
                    #     response_data["ethnicity"][p.ethnicity] = 0
                    # response_data["ethnicity"][p.ethnicity] += 1

                if p.birthday is None:
                    response_data["age"]["unspecified"] += 1
                else:
                    age_group = None
                    age = int((timezone.now() - p.birthday).days / 365.25)
                    if age < 18:
                        age_group = "0 - 17"
                    elif 18 <= age <= 24:
                        age_group = "18 - 24"
                    elif 25 <= age <= 34:
                        age_group = "25 - 34"
                    elif 35 <= age <= 44:
                        age_group = "35 - 44"
                    elif 45 <= age <= 54:
                        age_group = "45 - 54"
                    elif 55 <= age <= 64:
                        age_group = "55 - 64"
                    elif age > 64:
                        age_group = "65+"
                    if age_group not in response_data["age"]:
                        response_data["age"][age_group] = 0
                    response_data["age"][age_group] += 1
                    print(age)

        return Response(response_data)

    @detail_route(methods=['get'], url_path='discuss')
    def discuss(self, request, *args, **kwargs):
        project = self.get_object()

        url = project.discussion_link

        if project.discussion_link is None:
            client = DiscourseClient(
                settings.DISCOURSE_BASE_URL,
                api_username='system',
                api_key=settings.DISCOURSE_API_KEY)

            topic = client.create_topic(title=project.name, category=None)

            if topic is None:
                return Response(data={'status': 'request failed'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                url = '/t/%s/%d' % (topic['topic_slug'], topic['topic_id'])
                project.discussion_link = url
                project.save()

        topic_url = '%s%s' % (settings.DISCOURSE_BASE_URL, url)

        return Response({"link": topic_url, "id": project.id})


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(deleted_at__isnull=True)
    serializer_class = CategorySerializer

    @detail_route(methods=['post'])
    def update_category(self, request):
        category_serializer = CategorySerializer(data=request.data)
        category = self.get_object()
        if category_serializer.is_valid():
            category_serializer.update(category, category_serializer.validated_data)

            return Response({'status': 'updated category'})
        else:
            return Response(category_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            category = self.queryset
            categories_serialized = CategorySerializer(category, many=True)
            return Response(categories_serialized.data)
        except:
            return Response([])

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return Response({'status': 'deleted category'})
