import json
import math
from decimal import Decimal, ROUND_UP
from itertools import groupby
from textwrap import dedent

import numpy as np
from django.conf import settings
from crowdsourcing.discourse import DiscourseClient
from django.db import connection
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import mixins
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from yapf.yapflib.yapf_api import FormatCode

from crowdsourcing.models import Project, Task, TaskWorker, TaskWorkerResult
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator, ProjectChangesAllowed
from crowdsourcing.serializers.project import *
from crowdsourcing.serializers.task import *
from crowdsourcing.tasks import post_to_discourse
from crowdsourcing.utils import get_pk, get_template_tokens, SmallResultsSetPagination
from crowdsourcing.validators.project import validate_account_balance
from mturk.tasks import mturk_disable_hit


class ProjectViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Project.objects.active()
    serializer_class = ProjectSerializer
    pagination_class = SmallResultsSetPagination
    permission_classes = [IsProjectOwnerOrCollaborator, IsAuthenticated, ProjectChangesAllowed]

    def list(self, request, *args, **kwargs):
        account_type = request.query_params.get('account_type', 'worker')
        if account_type == 'worker':
            return self.worker_projects(request, args, kwargs)
        elif account_type == 'requester':
            return self.requester_projects(request, args, kwargs)
        return Response([])

    def create(self, request, *args, **kwargs):
        with_defaults = request.query_params.get('with_defaults', False)
        serializer = self.serializer_class(
            data=request.data,
            fields=('name', 'price', 'post_mturk', 'repetition', 'template'),
            context={'request': request}
        )

        if serializer.is_valid():
            with transaction.atomic():
                project = serializer.create(owner=request.user, with_defaults=with_defaults)

                serializer = ProjectSerializer(
                    instance=project,
                    fields=('id', 'name', 'template_id'),
                    context={'request': request}
                )

                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['post'], url_path='create-full')
    def create_full(self, request, *args, **kwargs):
        # price = request.data.get('price')
        # repetition = request.data.get('repetition', 1)
        # validate_account_balance(request, int(price * 100) * repetition)
        return self.create(request=request, with_defaults=False, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        serializer = ProjectSerializer(instance=self.get_object(),
                                       fields=('id', 'name', 'price', 'repetition', 'deadline', 'timeout',
                                               'is_prototype', 'template', 'status', 'post_mturk',
                                               'qualification', 'group_id', 'revisions', 'task_time',
                                               'has_review', 'parent', 'hash_id', 'is_api_only', 'batch_files',
                                               'aux_attributes', 'allow_price_per_task', 'task_price_field',
                                               'min_rating', 'publish_at', 'enable_boomerang'),
                                       context={'request': request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk, *args, **kwargs):
        with transaction.atomic():
            instance = Project.objects.select_for_update(nowait=True).get(id=pk)
            serializer = ProjectSerializer(
                instance=instance, data=request.data, partial=True, context={'request': request}
            )
            if serializer.is_valid():
                serializer.update()
            else:
                raise serializers.ValidationError(detail=serializer.errors)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

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

    @detail_route(methods=['POST'], url_path='log-preview', permission_classes=[IsAuthenticated])
    def log_preview(self, request, *args, **kwargs):
        project = self.get_object()
        models.ProjectPreview.objects.create(project=project, user=request.user)
        return Response({})

    @detail_route(methods=['PUT'])
    def update_status(self, request, pk, *args, **kwargs):
        with transaction.atomic():
            instance = self.queryset.select_for_update().get(id=pk)
            if request.data.get('status', Project.STATUS_IN_PROGRESS):
                total_needed = self.calculate_total(instance)
                to_pay = (Decimal(total_needed) - instance.amount_due).quantize(Decimal('.01'), rounding=ROUND_UP)
                validate_account_balance(request, to_pay)
                request.user.stripe_customer.account_balance -= int(to_pay * 100)
                request.user.stripe_customer.save()
                instance.amount_due += to_pay
            serializer = self.serializer_class(instance=instance, data=request.data)
            serializer.update_status()
        return Response({}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='payment')
    def payment(self, request, *args, **kwargs):
        instance = self.get_object()

        total_needed = self.calculate_total(instance)
        if total_needed is None:
            return Response({"to_pay": 0, "total": 0})
        to_pay = (Decimal(total_needed) - instance.amount_due).quantize(Decimal('.01'), rounding=ROUND_UP)
        return Response({"to_pay": to_pay, "total": total_needed})

    @detail_route(methods=['get'], url_path='submitted-tasks-count')
    def submitted_tasks_count(self, request, *args, **kwargs):
        instance = self.get_object()
        task_worker_count = TaskWorker.objects.filter(task__project__group_id=instance.group_id,
                                                      status=TaskWorker.STATUS_SUBMITTED).count()
        return Response({"submitted": task_worker_count})

    @staticmethod
    def calculate_total(instance):
        cursor = connection.cursor()
        # noinspection SqlResolve
        payment_query = '''
            WITH RECURSIVE cte(id, group_id, project_id, price, exclude_at, level) AS (
              SELECT
                t.id,
                t.group_id,
                project_id,
                coalesce(t.price, p.price) price,
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
                coalesce(t.price, p.price) price,
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
                                         coalesce(t.price, p.price) price,
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
        project_id, is_hash = get_pk(pk)
        filter_by = {}
        if is_hash:
            filter_by.update({'group_id': project_id})
        else:
            filter_by.update({'pk': project_id})

        with transaction.atomic():
            instance = self.queryset.select_for_update().filter(**filter_by).order_by('-id').first()
            # prototype task
            # if instance.is_prototype and instance.published_at is None:
            #     prototype_repetition = int(math.floor(math.sqrt(instance.repetition)))
            #     num_rows = int(math.floor(math.sqrt(instance.tasks.all().count())))
            #     instance.aux_attributes['repetition'] = instance.repetition
            #     instance.aux_attributes['number_of_tasks'] = instance.tasks.count()
            #     instance.save()
            #     instance.tasks.filter(row_number__gt=num_rows).delete()
            #     instance.repetition = prototype_repetition
            #     instance.save()
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

            total_needed = self.calculate_total(instance)
            to_pay = (Decimal(total_needed) - instance.amount_due).quantize(Decimal('.01'), rounding=ROUND_UP)
            instance.amount_due = total_needed if total_needed is not None else 0
            # if not instance.post_mturk:
            validate_account_balance(request, int(to_pay * 100))

            if serializer.is_valid():
                # with transaction.atomic():
                serializer.publish(to_pay)

                post_to_discourse.delay(instance.id)
            else:
                raise serializers.ValidationError(detail=serializer.errors)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['get'], url_path='for-workers')
    def worker_projects(self, request, *args, **kwargs):
        group_by = request.query_params.get('group_by', '-')
        # noinspection SqlResolve
        query = '''
            SELECT
              id,
              name,
              owner_id,
              status,
              round(price, 2),
              sum(paid_tasks) amount_paid,
              sum(task_price) expected_payout_amount,
              sum(returned)         returned,
              sum(in_progress)      in_progress,
              sum(accepted)         completed,
              sum(submitted)         awaiting_review,
              sum(paid_count)         paid_count,
              case when min(estimated_expire) < now() then null else min(estimated_expire) end expires_at,
              -- (max(submitted_at) + INTERVAL '1 day') payout_available_by
              case when (latest_charge + INTERVAL '2 day') < max(submitted_at)
              then  max(submitted_at) + INTERVAL '2 day'
              else
                 max(submitted_at) + INTERVAL '4 day'
               end payout_available_by,
               max(submitted_at) last_submitted_at
            FROM (SELECT
                    p.id                                                                      id,
                    p.name,
                    p.owner_id,
                    p.status,
                    p.price,
                    case when tw.status = %(accepted)s then coalesce(t.price, p.price) else 0 end paid_tasks,
                    coalesce(t.price, p.price) task_price,
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
                    ELSE 0 END                                                                       submitted,
                     CASE WHEN tw.is_paid is true
                      THEN 1
                    ELSE 0 END paid_count,
                    tw.submitted_at,
                    max(scharge.created_at) latest_charge
                  FROM crowdsourcing_taskworker tw
                    INNER JOIN crowdsourcing_task t ON tw.task_id = t.id
                    INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                    inner join crowdsourcing_stripecustomer sc on sc.owner_id = p.owner_id
                    left outer join crowdsourcing_stripecharge scharge on scharge.customer_id=sc.id
                    and scharge.created_at < p.revised_at
                  WHERE tw.status not in ((%(skipped)s), (%(expired)s))
                  AND tw.worker_id = (%(worker_id)s) AND p.is_review = FALSE
                  GROUP BY p.id,
                    p.name, p.owner_id, p.status, p.price,
                   tw.status, tw.is_paid, p.timeout, tw.started_at, tw.created_at, tw.submitted_at, t.price
                  ) tw
            GROUP BY tw.id, tw.name, tw.owner_id, tw.status, tw.price, latest_charge
            ORDER BY returned DESC, in_progress DESC, id DESC;
        '''
        projects = Project.objects.raw(query, params={
            'worker_id': request.user.id,
            'skipped': TaskWorker.STATUS_SKIPPED,
            'expired': TaskWorker.STATUS_EXPIRED,
            'in_progress': TaskWorker.STATUS_IN_PROGRESS,
            'returned': TaskWorker.STATUS_RETURNED,
            'accepted': TaskWorker.STATUS_ACCEPTED,
            'submitted': TaskWorker.STATUS_SUBMITTED,
            'default_timeout': '24 hour'
        })

        serializer = ProjectSerializer(instance=projects, many=True,
                                       fields=('id', 'name', 'owner', 'price', 'status', 'returned',
                                               'in_progress', 'awaiting_review', 'completed', 'expires_at',
                                               'payout_available_by', 'paid_count',
                                               'expected_payout_amount', 'amount_paid', 'last_submitted_at'),
                                       context={'request': request})
        if group_by == 'status':
            response_data = {
                "in_progress": [],
                "completed": [],
            }
            for p in serializer.data:
                if p['returned'] > 0 or p['in_progress'] > 0:
                    response_data['in_progress'].append(p)
                elif p['completed'] > 0 or p['awaiting_review'] > 0:
                    response_data['completed'].append(p)
        else:
            response_data = {
                "count": len(serializer.data),
                "next": None,
                "previous": None,
                "results": serializer.data
            }
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
              open_tasks as in_progress,
              checked_out
            FROM crowdsourcing_project p
              INNER JOIN (
                           SELECT
                             p_max.id  project_id,
                             sum(completed) completed,
                             sum(awaiting_review) awaiting_review,
                             greatest((p0.repetition * count(DISTINCT task_id)) - sum(completed) -
                               sum(awaiting_review), 0) - sum(checked_out) open_tasks,
                               sum(checked_out) checked_out
                           FROM (
                                  SELECT
                                    p.group_id,
                                    t.group_id task_id,
                                    CASE WHEN tw.status in (1, 5)
                                      THEN 1
                                    ELSE 0 END checked_out,
                                    CASE WHEN tw.status = 3
                                      THEN 1
                                    ELSE 0 END completed,
                                    CASE WHEN tw.status = 2
                                      THEN 1
                                    ELSE 0 END awaiting_review
                                  FROM crowdsourcing_project p
                                    LEFT OUTER JOIN crowdsourcing_task t ON t.project_id = p.id
                                      AND t.deleted_at IS NULL and t.exclude_at is null
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
                where p.deleted_at is NULL
            ORDER BY id DESC;
        '''
        projects = Project.objects.raw(query, params={'owner_id': request.user.id})
        serializer = ProjectSerializer(instance=projects, many=True,
                                       fields=('id', 'group_id', 'name', 'total_tasks', 'in_progress',
                                               'completed', 'awaiting_review', 'checked_out', 'status', 'price',
                                               'hash_id', 'min_rating', 'repetition', 'published_at',
                                               'revisions', 'updated_at', 'discussion_link'),
                                       context={'request': request})
        return Response({"count": len(serializer.data), "next": None, "previous": None, "results": serializer.data})

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

    @detail_route(methods=['get'], permission_classes=[])
    def preview(self, request, pk, *args, **kwargs):
        # project = self.get_object()
        project_id, is_hash = get_pk(pk)
        if is_hash:
            group_id = project_id
        else:
            group_id = Project.objects.get(id=project_id).group_id
        latest_revision = Project.objects.filter(group_id=group_id).order_by('-id').first()
        task = Task.objects.filter(project=latest_revision).first()
        task_serializer = TaskSerializer(instance=task, fields=('id', 'template'))
        return Response(data={
            "task": task_serializer.data,
            "name": latest_revision.name,
            "id": latest_revision.id,
            "price": task.price if task.price is not None else latest_revision.price,
            "status": latest_revision.status,
            "requester_handle": latest_revision.owner.profile.handle
        },
            status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='remaining-tasks')
    def tasks_remaining(self, request, pk, *args, **kwargs):
        project_id, is_hash = get_pk(pk)
        if is_hash:
            group_id = project_id
        else:
            group_id = Project.objects.get(id=project_id).group_id
        latest_revision = Project.objects.filter(group_id=group_id).order_by('-id').first()
        query = '''
            SELECT count(t.id) remaining
            FROM crowdsourcing_task t INNER JOIN (SELECT
                                                    group_id,
                                                    max(id) id
                                                  FROM crowdsourcing_task
                                                  WHERE deleted_at IS NULL
                                                  GROUP BY group_id) t_max ON t_max.id = t.id
              INNER JOIN crowdsourcing_project p ON p.id = t.project_id
              INNER JOIN (
                           SELECT
                             t.group_id,
                             sum(t.own)    own,
                             sum(t.others) others
                           FROM (
                                  SELECT
                                    t.group_id,
                                    CASE WHEN (tw.worker_id = %(worker_id)s AND tw.status <> 6)
                                              OR tw.is_qualified IS FALSE
                                      THEN 1
                                    ELSE 0 END own,
                                    CASE WHEN (tw.worker_id IS NOT NULL AND tw.worker_id <> %(worker_id)s)
                                              AND tw.status NOT IN (4, 6, 7)
                                      THEN 1
                                    ELSE 0 END others
                                  FROM crowdsourcing_task t
                                    LEFT OUTER JOIN crowdsourcing_taskworker tw ON (t.id =
                                                                                    tw.task_id)
                                  WHERE t.exclude_at IS NULL AND t.deleted_at IS NULL) t
                           GROUP BY t.group_id) t_count ON t_count.group_id = t.group_id
            WHERE t_count.own = 0 AND t_count.others < p.repetition AND p.id = %(project_id)s
        '''
        params = {
            "worker_id": request.user.id,
            "project_id": latest_revision.id,
        }
        cursor = connection.cursor()
        cursor.execute(query, params)
        remaining = cursor.fetchall()
        cursor.close()
        return Response({"remaining": remaining})

    @list_route(methods=['get'], url_path='task-feed')
    def task_feed(self, request, *args, **kwargs):
        sort_by = request.query_params.get('sort_by')
        user_preferences = request.user.preferences.aux_attributes
        if user_preferences is not None and user_preferences.get('sort_task_feed_by') is not None and sort_by == '-':
            sort_by = user_preferences.get('sort_task_feed_by')
        else:
            if sort_by == '-':
                sort_by = '-boomerang'
        if sort_by in ['-boomerang', '-published_at', '-price', '-available_tasks']:
            if user_preferences is None:
                user_preferences = {}
            user_preferences.update({"sort_task_feed_by": sort_by})
            request.user.preferences.save()
        projects = Project.objects.filter_by_boomerang(request.user, sort_by=sort_by)
        project_serializer = ProjectSerializer(instance=projects, many=True,
                                               fields=('id', 'name',
                                                       'timeout',
                                                       'available_tasks',
                                                       'price',
                                                       'task_time',
                                                       'aux_attributes',
                                                       'allow_price_per_task',
                                                       'discussion_link',
                                                       'requester_handle',
                                                       'requester_rating', 'raw_rating', 'is_prototype', 'is_review',),
                                               context={'request': request})

        return Response(data={"results": project_serializer.data, "sort_by": sort_by}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def comments(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectCommentSerializer(instance=instance.comments, many=True, fields=('comment', 'id',))
        response_data = {
            'project': kwargs['pk'],
            'comments': serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=[IsAuthenticated])
    def feedback(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectCommentSerializer(
            instance=instance.comments.filter(comment__sender=request.user).order_by('-id').first(),
            fields=('id', 'ready_for_launch', 'comment'))
        return Response(serializer.data, status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='post-comment', permission_classes=[IsAuthenticated])
    def post_comment(self, request, *args, **kwargs):
        serializer = ProjectCommentSerializer(data=request.data)
        comment_data = {}
        if serializer.is_valid():
            comment = serializer.create(project=kwargs['pk'], sender=request.user,
                                        ready_for_launch=request.data.get('ready_for_launch'))
            comment_data = ProjectCommentSerializer(
                comment,
                fields=('id', 'comment',),
                context={'request': request}).data

        return Response(data=comment_data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='update-comment', permission_classes=[IsAuthenticated])
    def update_comment(self, request, *args, **kwargs):
        project_comment = models.ProjectComment.objects \
            .filter(comment__sender=request.user,
                    project__group_id=self.get_object().group_id).order_by('-id').first()
        project_comment.ready_for_launch = request.data.get('ready_for_launch', project_comment.ready_for_launch)
        project_comment.comment.body = request.data.get('comment', {}).get('body')
        project_comment.comment.save()
        project_comment.save()
        return Response(data={"message": "Feedback updated"}, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def attach_file(self, request, **kwargs):
        serializer = ProjectBatchFileSerializer(data=request.data, fields=('batch_file',))
        if serializer.is_valid():
            project_file = serializer.create(project=kwargs['pk'])
            file_serializer = ProjectBatchFileSerializer(instance=project_file)
            ProjectSerializer().create_tasks(kwargs['pk'], False)
            # create_tasks_for_project.delay(kwargs['pk'], False)
            return Response(data=file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @detail_route(methods=['post'])
    def recreate_tasks(self, request, **kwargs):
        project = self.get_object()
        if project.status == Project.STATUS_DRAFT:
            ProjectSerializer().create_tasks(project.id, False)
        return Response(data={"message": "Tasks updated."}, status=status.HTTP_201_CREATED)

    @detail_route(methods=['delete'])
    def delete_file(self, request, **kwargs):
        batch_file = request.data.get('batch_file', None)
        instances = models.ProjectBatchFile.objects.filter(batch_file=batch_file)
        if instances.count() == 1:
            models.BatchFile.objects.filter(id=batch_file).delete()
        else:
            models.ProjectBatchFile.objects.filter(batch_file_id=batch_file, project_id=kwargs['pk']).delete()
        ProjectSerializer().create_tasks(kwargs['pk'], True)
        # create_tasks_for_project.delay(kwargs['pk'], True)
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
        # TODO select for update
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
        with transaction.atomic():
            project = self.queryset.filter(**filter_by).order_by('-id').first()

            existing_tasks = Task.objects.filter(project=project, rerun_key=run_key, exclude_at__isnull=True)

            task_objects = []
            all_hashes = [hash_task(data=task) for task in tasks if task]

            task_count = existing_tasks.count()
            existing_tasks.filter(hash__in=all_hashes).prefetch_related('task_workers')
            existing_hashes = existing_tasks.values_list('hash', flat=True)
            new_hashes = []

            row = 0
            response = {
                "project_key": pk,
                "tasks": []
            }
            to_pay = 0
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
                        to_pay += (price or project.price) * project.repetition
            if project.status != Project.STATUS_DRAFT:
                validate_account_balance(request, Decimal(to_pay).quantize(Decimal('.01'), rounding=ROUND_UP))
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
                request.user.stripe_customer.account_balance -= int(to_pay * 100)
                request.user.stripe_customer.save()
                project.amount_due += to_pay
                project.save()

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
    def rate_submissions_tabular(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        sort_by = request.query_params.get('sort_by')
        # group_by = 'worker_alias'
        if obj.aux_attributes is not None and obj.aux_attributes.get('sort_results_by') is not None and sort_by == '-':
            sort_by = obj.aux_attributes.get('sort_results_by')
        else:
            if sort_by == '-':
                sort_by = 'worker_id'

        if sort_by == 'worker_id':
            order_by_clause = (sort_by, '-submitted_at')
        elif sort_by == 'task_id':
            order_by_clause = (sort_by, '-submitted_at')
        else:
            order_by_clause = ('-submitted_at',)

        up_to = request.query_params.get('up_to')
        if up_to is None:
            up_to = timezone.now()
        task_workers = TaskWorker.objects.prefetch_related('worker', 'task', 'task__project', 'worker__profile') \
            .filter(
            status__in=[2, 3, 5],
            submitted_at__isnull=False,
            submitted_at__lte=up_to,
            task__project_id=obj.id).order_by(*order_by_clause)
        task_workers = self.paginate_queryset(task_workers)

        serializer = TaskWorkerSerializer(instance=task_workers, many=True,
                                          fields=('id', 'results', 'worker', 'status', 'task',
                                                  'worker_alias', 'worker_rating', 'attempt',
                                                  'submitted_at', 'approved_at', 'task_data', 'task_template'))

        response = self.get_paginated_response(serializer.data)
        if sort_by == 'worker_id':
            grouped_responses = self._group_by_worker(response.data['results'])
        else:
            grouped_responses = response.data['results']

        if obj.aux_attributes is None:
            obj.aux_attributes = {}
        obj.aux_attributes['sort_results_by'] = sort_by
        obj.save()
        # group_by_worker.sort(key=lambda x: x['tasks'].count, reverse=True)
        return Response(
            data={"workers": grouped_responses, "count": response.data['count'], "next": response.data['next'],
                  "up_to": up_to,
                  "project_template": TemplateSerializer(instance=obj.template).data, 'sort_by': sort_by},
            status=status.HTTP_200_OK)

    @staticmethod
    def _group_by_worker(data):
        group_by_worker = []
        for key, group in groupby(data, lambda x: x['worker_alias']):
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
        return group_by_worker

    @detail_route(methods=['get'], url_path='last-opened')
    def last_opened(self, request, *args, **kwargs):
        project = self.get_object()
        last_opened_at = copy.copy(project.last_opened_at)
        project.last_opened_at = timezone.now()
        project.save()
        return Response({"last_opened_at": last_opened_at, "id": project.id})

    @detail_route(methods=['get'], url_path='worker-demographics')
    def worker_statistics(self, request, *args, **kwargs):
        project = self.get_object()
        worker_ids = TaskWorker.objects.prefetch_related('worker__profile').filter(
            task__project__group_id=project.group_id,
            status__in=[TaskWorker.STATUS_SUBMITTED, TaskWorker.STATUS_ACCEPTED,
                        TaskWorker.STATUS_RETURNED]).values_list('worker_id', flat=True)
        profiles = models.UserProfile.objects.prefetch_related('address__city').filter(user_id__in=worker_ids)
        response_data = {
            "results": 0,
            "education": {
                "Unspecified": 0
            },
            "gender": {
                "Unspecified": 0
            },
            "ethnicity": {
                "Unspecified": 0
            },
            "age": {
                "Unspecified": 0
            },
            "location": {
                "Unspecified": 0
            }
        }
        if len(profiles) >= settings.MIN_WORKERS_FOR_STATS:
            for p in profiles:
                response_data["results"] += 1
                if p.education is None:
                    response_data["education"]["Unspecified"] += 1
                else:
                    if p.get_education_display() not in response_data["education"]:
                        response_data["education"][p.get_education_display()] = 0
                    response_data["education"][p.get_education_display()] += 1

                if p.ethnicity is None:
                    response_data["ethnicity"]["Unspecified"] += 1
                else:
                    if p.get_ethnicity_display() not in response_data["ethnicity"]:
                        response_data["ethnicity"][p.get_ethnicity_display()] = 0
                    response_data["ethnicity"][p.get_ethnicity_display()] += 1
                if p.gender is None:
                    response_data["gender"]["Unspecified"] += 1
                else:
                    if p.get_gender_display() not in response_data["gender"]:
                        response_data["gender"][p.get_gender_display()] = 0
                    response_data["gender"][p.get_gender_display()] += 1
                if p.address is None:
                    response_data["location"]["Unspecified"] += 1
                else:
                    location = p.address.city.state_code
                    if location not in response_data["location"]:
                        response_data["location"][location] = 0
                    response_data["location"][location] += 1

                if p.birthday is None:
                    response_data["age"]["Unspecified"] += 1
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

        return Response(response_data)

    @detail_route(methods=['get'], url_path='discuss')
    def discuss(self, request, *args, **kwargs):
        project = self.get_object()
        url = project.discussion_link
        aux_attrib = project.aux_attributes

        try:
            if url is None:
                # post topic as system user
                client = DiscourseClient(
                    settings.DISCOURSE_BASE_URL,
                    api_username='system',
                    api_key=settings.DISCOURSE_API_KEY)

                if 'median_price' in aux_attrib:
                    price = aux_attrib['median_price']

                    if price is not None and float(price) > 0:
                        price = float(price)
                    else:
                        price = project.price
                else:
                    price = project.price

                topic = client.create_topic(title=project.name,
                                            category=settings.DISCOURSE_TOPIC_TASKS,
                                            timeout=project.timeout,
                                            price=price,
                                            requester_handle=project.owner.profile.handle,
                                            project_id=project.id)

                if topic is None:
                    return Response(data={'status': 'request failed'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    url = '/t/%s/%d' % (topic['topic_slug'], topic['topic_id'])
                    project.discussion_link = url
                    project.topic_id = topic['topic_id']
                    project.post_id = topic['id']
                    project.save()

                    # watch as requester
                    client = DiscourseClient(
                        settings.DISCOURSE_BASE_URL,
                        api_username=project.owner.profile.handle,
                        api_key=settings.DISCOURSE_API_KEY)

                    client.watch_topic(topic_id=topic['topic_id'])

        except Exception as e:
            return Response(data={'status': 'request failed: %s' % e.message}, status=status.HTTP_400_BAD_REQUEST)

        topic_url = '%s%s' % (settings.DISCOURSE_BASE_URL, url)
        return HttpResponseRedirect('%s' % topic_url)

    # noinspection PyTypeChecker
    @detail_route(methods=['get'], url_path='time-estimate', permission_classes=[IsAuthenticated])
    def time_estimate(self, request, *args, **kwargs):
        project = self.get_object()
        other_workers = TaskWorker.objects.filter(~Q(worker=request.user), submitted_at__isnull=False,
                                                  task__project__group_id=project.group_id,
                                                  status__in=[TaskWorker.STATUS_ACCEPTED, TaskWorker.STATUS_SUBMITTED])
        this_worker = TaskWorker.objects.filter(worker=request.user, submitted_at__isnull=False,
                                                task__project__group_id=project.group_id,
                                                status__in=[TaskWorker.STATUS_ACCEPTED, TaskWorker.STATUS_SUBMITTED])

        others_time = [(ow.submitted_at - ow.created_at).total_seconds() for ow in other_workers]
        this_time = [(tw.submitted_at - tw.created_at).total_seconds() for tw in this_worker]
        return Response(
            {"self_time_estimate": math.ceil(np.median(this_time)) if this_time else None,
             "others_time_estimate": math.ceil(np.median(others_time)) if others_time else None})

    @list_route(methods=['get'], url_path='workers')
    def workers(self, request, *args, **kwargs):
        topic = request.query_params.get('topic_id')
        project = Project.objects.filter(topic_id=topic).first()
        if project is None:
            return Response({"message": "Project not found"}, 404)
        workers = TaskWorker.objects.prefetch_related('worker__profile') \
            .values('worker__profile').distinct().filter(
            status__in=[TaskWorker.STATUS_RETURNED, TaskWorker.STATUS_ACCEPTED, TaskWorker.STATUS_SUBMITTED],
            task__project__group_id=project.group_id).values_list('worker__profile__handle', flat=True)
        return Response(workers)

    @detail_route(methods=['get'], url_path='tasks')
    def tasks(self, request, *args, **kwargs):
        tasks = self.get_object().tasks.all()

        return Response({
            "count": tasks.count(),
            "next": None,
            "previous": None,
            "results": TaskSerializer(instance=tasks, many=True,
                                      fields=('id', 'group_id', 'data', 'hash', 'project',
                                              'created_at', 'price', 'row_number')).data
        })

    @detail_route(methods=['get'], url_path='assignment-results')
    def assignment_results(self, request, pk, *args, **kwargs):
        results = TaskWorkerResult.objects.filter(task_worker__task__project_id=pk)
        response_data = TaskWorkerResultSerializer(instance=results,
                                                   many=True,
                                                   fields=('id', 'template_item', 'result',
                                                           'created_at', 'updated_at', 'attachment',
                                                           'assignment_id')).data
        return Response(response_data)
