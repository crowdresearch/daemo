import datetime
import json
from urlparse import urlsplit

from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import utc
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

from crowdsourcing import constants
from crowdsourcing.models import Task, TaskWorker, TaskWorkerResult, UserPreferences, ReturnFeedback
from crowdsourcing.permissions.task import HasExceededReservedLimit, IsTaskOwner
from crowdsourcing.permissions.util import IsSandbox
from crowdsourcing.serializers.project import ProjectSerializer
from crowdsourcing.serializers.task import *
from crowdsourcing.tasks import update_worker_cache, post_approve, refund_task
from crowdsourcing.utils import get_model_or_none
from mturk.tasks import mturk_hit_update, mturk_approve


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_params = ['project_id', 'rerun_key', 'batch_id']

    def list(self, request, *args, **kwargs):
        try:
            by = request.query_params.get('filter_by', 'project_id')
            if by not in self.filter_params:
                return Response(data={"message": "Invalid filter by field."}, status=status.HTTP_400_BAD_REQUEST)
            filter_value = request.query_params.get(by, -1)
            task = Task.objects.filter(**{by: filter_value}).order_by('row_number')
            task_serialized = TaskSerializer(task, many=True,
                                             fields=('id', 'data', 'batch', 'project_data', 'row_number'))
            return Response(task_serialized.data)
        except:
            return Response([])

    @list_route(methods=['get'], url_path='list-data')
    def list_conflicts(self, request, *args, **kwargs):
        project = request.query_params.get('project', -1)
        offset = int(request.query_params.get('offset', 0))

        # noinspection SqlResolve
        query = '''
            SELECT t.id, t.data, t.row_number
            FROM crowdsourcing_task t
              INNER JOIN (

                           SELECT t.group_id, count(tw.id)
                           FROM crowdsourcing_task t
                             LEFT OUTER JOIN crowdsourcing_taskworker tw ON (t.id = tw.task_id
                             AND tw.status NOT IN (4, 6, 7))
                           WHERE exclude_at IS NULL AND t.deleted_at IS NULL AND t.project_id <> (%(project_id)s)
                           GROUP BY t.group_id HAVING count(tw.id)>0) all_tasks ON all_tasks.group_id = t.group_id
            WHERE project_id = (%(project_id)s) AND deleted_at IS NULL
            LIMIT 10 OFFSET (%(seek)s)
        '''

        tasks = list(Task.objects.raw(query, params={'project_id': project, 'seek': offset}))
        headers = []
        if len(tasks) > 0:
            headers = tasks[0].data.keys()[:4]
        serializer = TaskSerializer(tasks, many=True, fields=('id', 'data', 'row_number'))
        return Response({'headers': headers, 'tasks': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        object = self.get_object()
        serializer = TaskSerializer(instance=object, fields=('id', 'template', 'project_data',
                                                             'worker_count', 'completed', 'total'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        task.delete()
        return Response({'status': 'deleted task'})

    @detail_route(methods=['get'])
    def retrieve_with_data(self, request, *args, **kwargs):
        task = self.get_object()
        task_worker = TaskWorker.objects.filter(worker=request.user, task=task).first()
        serializer = TaskSerializer(instance=task,
                                    fields=('id', 'template', 'project_data', 'status', 'has_comments'),
                                    context={'task_worker': task_worker})
        requester_alias = task.project.owner.username
        project = task.project.id
        target = task.project.owner.id
        timeout = task.project.timeout
        worker_timestamp = task_worker.created_at
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if timeout is not None:
            time_left = int((timeout * 60) - (now - worker_timestamp).total_seconds())
        else:
            time_left = None

        auto_accept = False
        user_prefs = get_model_or_none(UserPreferences, user=request.user)
        if user_prefs is not None:
            auto_accept = user_prefs.auto_accept

        return Response({'data': serializer.data,
                         'requester_alias': requester_alias,
                         'project': project,
                         'time_left': time_left,
                         'auto_accept': auto_accept,
                         'task_worker_id': task_worker.id,
                         'target': target}, status.HTTP_200_OK)

    @list_route(methods=['get'])
    def list_by_project(self, request, **kwargs):
        tasks = Task.objects.filter(project=request.query_params.get('project_id')).order_by('id')
        task_serializer = TaskSerializer(instance=tasks, many=True, fields=('id', 'updated_at',
                                                                            'worker_count', 'completed', 'total'))
        return Response(data=task_serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def list_comments(self, request, **kwargs):
        comments = models.TaskComment.objects.filter(task=kwargs['pk'])
        serializer = TaskCommentSerializer(instance=comments, many=True, fields=('comment', 'id',))
        response_data = {
            'task': kwargs['pk'],
            'comments': serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def post_comment(self, request, **kwargs):
        serializer = TaskCommentSerializer(data=request.data)
        task_comment_data = {}
        if serializer.is_valid():
            comment = serializer.create(task=kwargs['pk'], sender=request.user)
            task_comment_data = TaskCommentSerializer(comment, fields=('id', 'comment',)).data

        return Response(task_comment_data, status.HTTP_200_OK)

    @list_route(methods=['post'], url_path='relaunch-all')
    def relaunch_all(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', -1)
        project = get_object_or_404(models.Project, pk=project_id)
        tasks = models.Task.objects.active().filter(~Q(project_id=project_id), project__group_id=project.group_id)
        self.serializer_class().bulk_update(tasks, {'exclude_at': project_id})
        return Response(data={}, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='relaunch')
    def relaunch(self, request, *args, **kwargs):
        task = self.get_object()
        tasks = models.Task.objects.active().filter(~Q(id=task.id), group_id=task.group_id)
        self.serializer_class().bulk_update(tasks, {'exclude_at': task.project_id})
        return Response(data={}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='is-done')
    def is_done(self, request, *args, **kwargs):
        group_id = self.get_object().group_id
        # noinspection SqlResolve
        query = '''
            SELECT count(t.id) remaining
            FROM crowdsourcing_task t
              INNER JOIN (SELECT
                            group_id,
                            max(id) id
                          FROM crowdsourcing_task
                          WHERE deleted_at IS NULL
                          GROUP BY group_id) t_max ON t_max.id = t.id
              INNER JOIN crowdsourcing_project p ON p.id = t.project_id
              INNER JOIN (
                           SELECT
                             t.group_id,
                             sum(t.others) OTHERS
                           FROM (
                                  SELECT
                                    t.group_id,
                                    CASE WHEN tw.id IS NOT NULL
                                      THEN 1
                                    ELSE 0 END OTHERS
                                  FROM crowdsourcing_task t
                                    LEFT OUTER JOIN crowdsourcing_taskworker tw
                                      ON (t.id = tw.task_id AND tw.status IN (2, 3))
                                  WHERE t.exclude_at IS NULL AND t.deleted_at IS NULL) t
                           GROUP BY t.group_id) t_count ON t_count.group_id = t.group_id
            WHERE t_count.others < p.repetition AND t.group_id = (%(group_id)s);
        '''
        cursor = connection.cursor()
        cursor.execute(query, {'group_id': group_id})
        remaining_count = cursor.fetchall()[0][0] if cursor.rowcount > 0 else 0
        return Response(data={"is_done": remaining_count == 0}, status=status.HTTP_200_OK)


class TaskWorkerViewSet(viewsets.ModelViewSet):
    queryset = TaskWorker.objects.all()
    serializer_class = TaskWorkerSerializer
    permission_classes = [IsAuthenticated, HasExceededReservedLimit]

    # lookup_field = 'task__id'

    def create(self, request, *args, **kwargs):
        serializer = TaskWorkerSerializer()
        instance, http_status = serializer.create(worker=request.user,
                                                  project=request.data.get('project', None))
        serialized_data = {}
        if http_status == 200:
            serialized_data = TaskWorkerSerializer(instance=instance, fields=('id', 'task')).data
            update_worker_cache.delay([instance.worker_id], constants.TASK_ACCEPTED)
            mturk_hit_update.delay({'id': instance.task.id})
        return Response(serialized_data, http_status)

    def destroy(self, request, *args, **kwargs):
        serializer = TaskWorkerSerializer()
        obj = self.queryset.get(id=kwargs['pk'], worker=request.user)
        auto_accept = False
        user_prefs = get_model_or_none(UserPreferences, user=request.user)
        instance, http_status = None, status.HTTP_204_NO_CONTENT
        if user_prefs is not None:
            auto_accept = user_prefs.auto_accept
        if auto_accept:
            instance, http_status = serializer.create(worker=request.user, project=obj.task.project_id)
        obj.status = TaskWorker.STATUS_SKIPPED
        obj.save()
        refund_task.delay([{'id': obj.id}])
        update_worker_cache.delay([obj.worker_id], constants.TASK_SKIPPED)
        mturk_hit_update.delay({'id': obj.task.id})
        serialized_data = {}
        if http_status == status.HTTP_200_OK:
            serialized_data = TaskWorkerSerializer(instance=instance).data
        return Response(serialized_data, http_status)

    @list_route(methods=['post'], url_path='bulk-update-status')
    def bulk_update_status(self, request, *args, **kwargs):
        task_status = request.data.get('status', -1)
        task_workers = TaskWorker.objects.filter(id__in=tuple(request.data.get('workers', [])))
        task_workers.update(status=task_status, updated_at=timezone.now())
        workers = task_workers.values_list('worker_id', flat=True)
        if task_status == TaskWorker.STATUS_RETURNED:
            update_worker_cache.delay(list(workers), constants.TASK_RETURNED)
        elif task_status == TaskWorker.STATUS_REJECTED:
            update_worker_cache.delay(list(workers), constants.TASK_REJECTED)
        return Response(TaskWorkerSerializer(instance=task_workers, many=True,
                                             fields=('id', 'task', 'status',
                                                     'worker_alias', 'updated_delta')).data, status.HTTP_200_OK)

    @list_route(methods=['post'], url_path='accept-all')
    def accept_all(self, request, *args, **kwargs):
        task_id = request.query_params.get('task_id', -1)
        from itertools import chain
        task_workers = TaskWorker.objects.filter(status=TaskWorker.STATUS_SUBMITTED, task_id=task_id)
        list_workers = list(chain.from_iterable(task_workers.values_list('id')))
        update_worker_cache.delay(list(task_workers.values_list('worker_id', flat=True)), constants.TASK_APPROVED)
        task_workers.update(status=TaskWorker.STATUS_ACCEPTED, updated_at=timezone.now())
        post_approve.delay(task_id, len(list_workers))
        mturk_approve.delay(list_workers)
        return Response(data=list_workers, status=status.HTTP_200_OK)

    @list_route(methods=['get'], url_path='list-my-tasks')
    def list_my_tasks(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id', -1)
        task_workers = TaskWorker.objects.exclude(status=TaskWorker.STATUS_SKIPPED). \
            filter(worker=request.user, task__project_id=project_id)
        serializer = TaskWorkerSerializer(instance=task_workers, many=True,
                                          fields=(
                                              'id', 'status', 'task',
                                              'is_paid', 'return_feedback'))
        response_data = {
            "project_id": project_id,
            "tasks": serializer.data
        }
        return Response(data=response_data, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def drop_saved_tasks(self, request, *args, **kwargs):
        task_ids = request.data.get('task_ids', [])
        for task_id in task_ids:
            mturk_hit_update.delay({'id': task_id})
        task_workers = self.queryset.filter(task_id__in=task_ids, worker=request.user)
        task_workers.update(
            status=TaskWorker.STATUS_SKIPPED, updated_at=timezone.now())
        tw_serialized = self.serializer_class(task_workers, fields=('id',), many=True).data
        refund_task.delay(tw_serialized)
        return Response(data={'task_ids': task_ids}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def bulk_pay_by_project(self, request, *args, **kwargs):
        project = request.data.get('project')
        task_workers = TaskWorker.objects.filter(task__project=project).filter(
            Q(status=TaskWorker.STATUS_ACCEPTED) | Q(status=TaskWorker.STATUS_REJECTED))
        task_workers.update(is_paid=True, updated_at=timezone.now())
        return Response('Success', status.HTTP_200_OK)

    @list_route(methods=['get'], url_path="list-submissions")
    def list_submissions(self, request, *args, **kwargs):
        task_id = request.query_params.get('task_id', -1)
        workers = TaskWorker.objects.filter(status__in=[2, 3, 5], task_id=task_id)
        serializer = TaskWorkerSerializer(instance=workers, many=True,
                                          fields=('id', 'results',
                                                  'worker_alias', 'worker_rating', 'worker', 'status'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class TaskWorkerResultViewSet(viewsets.ModelViewSet):
    queryset = TaskWorkerResult.objects.all()
    serializer_class = TaskWorkerResultSerializer

    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        task_worker_result = self.queryset.filter(id=kwargs['pk'])[0]
        status = TaskWorkerResult.STATUS_CREATED

        if 'status' in request.data:
            status = request.data['status']

        task_worker_result.status = status
        task_worker_result.save()
        return Response("Success")

    def retrieve(self, request, *args, **kwargs):
        result = self.get_object()
        serializer = TaskWorkerResultSerializer(instance=result)
        return Response(serializer.data)

    @list_route(methods=['post'], url_path="submit-results")
    def submit_results(self, request, mock=False, *args, **kwargs):
        task = request.data.get('task', None)
        auto_accept = request.data.get('auto_accept', False)
        template_items = request.data.get('items', [])
        task_status = request.data.get('status', None)
        saved = request.data.get('saved')
        task_worker = None
        if mock:
            task_status = TaskWorker.STATUS_SUBMITTED
            template_items = kwargs['items']
            task_worker = kwargs['task_worker']

        with transaction.atomic():
            if not mock:
                task_worker = TaskWorker.objects.prefetch_related('task', 'task__project').get(worker=request.user,
                                                                                               task=task)
            task_worker_results = TaskWorkerResult.objects.filter(task_worker_id=task_worker.id)

            if task_status == TaskWorker.STATUS_IN_PROGRESS:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True, partial=True)
            else:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True)

            if serializer.is_valid():
                task_worker.status = task_status
                task_worker.save()
                if task_status == TaskWorker.STATUS_SUBMITTED:
                    redis_publisher = RedisPublisher(facility='bot', users=[task_worker.task.project.owner])

                    message = RedisMessage(json.dumps({
                        'project_id': task_worker.task.project_id,
                        'project_hash_id': ProjectSerializer().get_hash_id(task_worker.task.project),
                        'task_id': task_worker.task_id,
                        'taskworker_id': task_worker.id,
                        'worker_id': task_worker.worker_id,
                        'batch': {
                            'id': task_worker.task.batch_id,
                            'parent': task_worker.task.batch.parent if task_worker.task.batch is not None else None,
                        }
                    }))

                    redis_publisher.publish_message(message)
                if task_worker_results.count() != 0:
                    serializer.update(task_worker_results, serializer.validated_data)
                else:
                    serializer.create(task_worker=task_worker)

                update_worker_cache.delay([task_worker.worker_id], constants.TASK_SUBMITTED)

                if task_status == TaskWorker.STATUS_IN_PROGRESS or saved or mock:
                    return Response('Success', status.HTTP_200_OK)
                elif task_status == TaskWorker.STATUS_SUBMITTED and not saved:

                    if not auto_accept:
                        serialized_data = {}
                        http_status = 204
                        return Response(serialized_data, http_status)

                    task_worker_serializer = TaskWorkerSerializer()
                    instance, http_status = task_worker_serializer.create(
                        worker=request.user, project=task_worker.task.project_id)
                    serialized_data = {}

                    if http_status == status.HTTP_200_OK:
                        serialized_data = TaskWorkerSerializer(instance=instance).data
                        update_worker_cache.delay([task_worker.worker_id], constants.TASK_ACCEPTED)

                    return Response(serialized_data, http_status)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'], url_path="mock-results", permission_classes=[IsSandbox, IsTaskOwner])
    def mock_results(self, request, *args, **kwargs):
        task_id = request.data.get('task_id', None)
        results = request.data.get('results', [])
        existing_workers = TaskWorker.objects.values('worker') \
            .filter(task_id=task_id,
                    status__in=[TaskWorker.STATUS_ACCEPTED,
                                TaskWorker.STATUS_IN_PROGRESS,
                                TaskWorker.STATUS_SUBMITTED,
                                TaskWorker.STATUS_RETURNED]).values_list(
            'worker', flat=True)
        new_workers = User.objects.filter(~Q(id__in=existing_workers),
                                          username__startswith='mockworker.')[:len(results)]
        for i, worker in enumerate(new_workers):
            task_worker, created = TaskWorker.objects.get_or_create(worker=worker, task_id=task_id)
            self.submit_results(request, mock=True, items=results[i]['items'], task_worker=task_worker)
        return Response(data={"message": "{} results submitted".format(len(new_workers))},
                        status=status.HTTP_201_CREATED)


class ExternalSubmit(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        identifier = request.query_params.get('daemo_id', False)
        if not identifier:
            return Response("Missing identifier", status=status.HTTP_400_BAD_REQUEST)
        try:
            from django.conf import settings
            from hashids import Hashids
            identifier_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
            if len(identifier_hash.decode(identifier)) == 0:
                return Response("Invalid identifier", status=status.HTTP_400_BAD_REQUEST)
            task_worker_id, task_id, template_item_id = identifier_hash.decode(identifier)
            template_item = models.TemplateItem.objects.get(id=template_item_id)
            task = models.Task.objects.get(id=task_id)
            source_url = None
            if template_item.aux_attributes['src']:
                source_url = urlsplit(template_item.aux_attributes['src'])
            else:
                source_url = urlsplit(task.data[template_item.aux_attributes['data_source']])
            if 'HTTP_REFERER' not in request.META.keys():
                return Response(data={"message": "Missing referer"}, status=status.HTTP_403_FORBIDDEN)
            referer_url = urlsplit(request.META['HTTP_REFERER'])
            if referer_url.netloc != source_url.netloc or referer_url.scheme != source_url.scheme:
                return Response(data={"message": "Referer does not match source"}, status=status.HTTP_403_FORBIDDEN)

            redis_publisher = RedisPublisher(facility='external', broadcast=True)
            task_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
            message = RedisMessage(json.dumps({"task_id": task_hash.encode(task_id),
                                               "daemo_id": identifier,
                                               "template_item": template_item_id
                                               }))
            redis_publisher.publish_message(message)
            with transaction.atomic():
                task_worker = TaskWorker.objects.get(id=task_worker_id, task_id=task_id)
                task_worker_result, created = TaskWorkerResult.objects.get_or_create(task_worker_id=task_worker.id,
                                                                                     template_item_id=template_item_id)
                # only accept in progress, submitted, or returned tasks
                if task_worker.status in [1, 2, 5]:
                    task_worker_result.result = request.data
                    task_worker_result.save()
                    update_worker_cache.delay([task_worker.worker_id], constants.TASK_SUBMITTED)
                    return Response(request.data, status=status.HTTP_200_OK)
                else:
                    return Response("Task cannot be modified now", status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response("Invalid identifier", status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)


class ReturnFeedbackViewSet(viewsets.ModelViewSet):
    queryset = ReturnFeedback.objects.all()
    serializer_class = ReturnFeedbackSerializer

    def create(self, request, *args, **kwargs):
        serializer = ReturnFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
