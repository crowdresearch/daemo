import datetime
import json
from urlparse import urlsplit

from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import utc
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

from ws4redis.publisher import RedisPublisher

from ws4redis.redis_store import RedisMessage

from crowdsourcing.serializers.task import *
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.models import Task, TaskWorker, TaskWorkerResult, UserPreferences
from crowdsourcing.permissions.task import HasExceededReservedLimit
from crowdsourcing.utils import get_model_or_none
from mturk.tasks import mturk_hit_update, mturk_approve


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @detail_route(methods=['post'], permission_classes=[IsProjectOwnerOrCollaborator])
    def update_task(self, request, id=None):
        task_serializer = TaskSerializer(data=request.data)
        task = self.get_object()
        if task_serializer.is_valid():
            task_serializer.update(task, task_serializer.validated_data)
            return Response({'status': 'updated task'})
        else:
            return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            project = request.query_params.get('project')
            task = Task.objects.filter(project=project)
            task_serialized = TaskSerializer(task, many=True)
            return Response(task_serialized.data)
        except:
            return Response([])

    def retrieve(self, request, *args, **kwargs):
        object = self.get_object()
        serializer = TaskSerializer(instance=object, fields=('id', 'template', 'project_data',
                                                             'worker_count', 'completion'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        task_serializer = TaskSerializer()
        task = self.get_object()
        task_serializer.delete(task)
        return Response({'status': 'deleted task'})

    @detail_route(methods=['get'])
    def retrieve_with_data(self, request, *args, **kwargs):
        task = self.get_object()
        task_worker = TaskWorker.objects.filter(worker=request.user.userprofile.worker, task=task).first()
        serializer = TaskSerializer(instance=task,
                                    fields=('id', 'template', 'project_data', 'status', 'has_comments'),
                                    context={'task_worker': task_worker})
        requester_alias = task.project.owner.alias
        project = task.project.id
        target = task.project.owner.profile.id
        timeout = task.project.timeout
        worker_timestamp = task_worker.created_timestamp
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
                         'target': target}, status.HTTP_200_OK)

    @list_route(methods=['get'])
    def list_by_project(self, request, **kwargs):
        tasks = Task.objects.filter(project=request.query_params.get('project_id'))
        task_serializer = TaskSerializer(instance=tasks, many=True, fields=('id', 'last_updated',
                                                                            'worker_count', 'completion'))
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
            comment = serializer.create(task=kwargs['pk'], sender=request.user.userprofile)
            task_comment_data = TaskCommentSerializer(comment, fields=('id', 'comment',)).data

        return Response(task_comment_data, status.HTTP_200_OK)


class TaskWorkerViewSet(viewsets.ModelViewSet):
    queryset = TaskWorker.objects.all()
    serializer_class = TaskWorkerSerializer
    permission_classes = [IsAuthenticated, HasExceededReservedLimit]
    lookup_field = 'task__id'

    def create(self, request, *args, **kwargs):
        serializer = TaskWorkerSerializer()
        instance, http_status = serializer.create(worker=request.user.userprofile.worker,
                                                  project=request.data.get('project', None))
        serialized_data = {}
        if http_status == 200:
            serialized_data = TaskWorkerSerializer(instance=instance).data
            mturk_hit_update.delay({'id': instance.task.id})
        return Response(serialized_data, http_status)

    def destroy(self, request, *args, **kwargs):
        serializer = TaskWorkerSerializer()
        obj = self.queryset.get(task=kwargs['task__id'], worker=request.user.userprofile.worker.id)
        instance, http_status = serializer.create(worker=request.user.userprofile.worker, project=obj.task.project_id)
        obj.task_status = TaskWorker.STATUS_SKIPPED
        obj.save()
        mturk_hit_update.delay({'id': obj.task.id})
        serialized_data = {}
        if http_status == status.HTTP_200_OK:
            serialized_data = TaskWorkerSerializer(instance=instance).data
        return Response(serialized_data, http_status)

    @list_route(methods=['post'])
    def bulk_update_status(self, request, *args, **kwargs):
        task_status = request.data.get('task_status', -1)
        task_workers = TaskWorker.objects.filter(id__in=tuple(request.data.get('task_workers', [])))
        task_workers.update(task_status=task_status, last_updated=timezone.now())
        return Response(TaskWorkerSerializer(instance=task_workers, many=True,
                                             fields=('id', 'task', 'task_status',
                                                     'worker_alias', 'updated_delta')).data, status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='accept-all')
    def accept_all(self, request, *args, **kwargs):
        from itertools import chain
        task_workers = TaskWorker.objects.filter(task_status=TaskWorker.STATUS_SUBMITTED, task_id=kwargs['task__id'])
        list_workers = list(chain.from_iterable(task_workers.values_list('id')))
        task_workers.update(task_status=TaskWorker.STATUS_ACCEPTED, last_updated=timezone.now())
        mturk_approve.delay(list_workers)
        return Response(data=list_workers, status=status.HTTP_200_OK)

    @list_route(methods=['get'], url_path='list-my-tasks')
    def list_my_tasks(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id', -1)
        task_workers = TaskWorker.objects.exclude(task_status=TaskWorker.STATUS_SKIPPED). \
            filter(worker=request.user.userprofile.worker, task__project_id=project_id)
        serializer = TaskWorkerSerializer(instance=task_workers, many=True,
                                          fields=(
                                              'id', 'task_status', 'task',
                                              'is_paid'))
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
        self.queryset.filter(task_id__in=task_ids, worker=request.user.userprofile.worker.id).update(
            task_status=TaskWorker.STATUS_SKIPPED, last_updated=timezone.now())
        return Response('Success', status.HTTP_200_OK)

    @list_route(methods=['post'])
    def bulk_pay_by_project(self, request, *args, **kwargs):
        project = request.data.get('project')
        task_workers = TaskWorker.objects.filter(task__project=project).filter(
            Q(task_status=TaskWorker.STATUS_ACCEPTED) | Q(task_status=TaskWorker.STATUS_REJECTED))
        task_workers.update(is_paid=True, last_updated=timezone.now())
        return Response('Success', status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path="list-submissions")
    def list_submissions(self, request, *args, **kwargs):
        workers = TaskWorker.objects.filter(task_status__in=[2, 3, 5], task_id=kwargs.get('task__id', -1))
        serializer = TaskWorkerSerializer(instance=workers, many=True,
                                          fields=('id', 'task_worker_results',
                                                  'worker_alias', 'worker_rating', 'worker', 'task_status'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class TaskWorkerResultViewSet(viewsets.ModelViewSet):
    queryset = TaskWorkerResult.objects.all()
    serializer_class = TaskWorkerResultSerializer

    # permission_classes = [IsOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        task_worker_result = self.queryset.filter(id=kwargs['pk'])[0]
        status = TaskWorkerResult.STATUS_CREATED

        if 'status' in request.data:
            status = request.data['status']

        task_worker_result.status = status
        task_worker_result.save()
        return Response("Success")

    def retrieve(self, request, *args, **kwargs):
        worker = get_object_or_404(self.queryset, worker=request.worker)
        serializer = TaskWorkerResultSerializer(instance=worker)
        return Response(serializer.data)

    @list_route(methods=['post'], url_path="submit-results")
    def submit_results(self, request, *args, **kwargs):
        task = request.data.get('task', None)
        auto_accept = request.data.get('auto_accept', False)
        template_items = request.data.get('template_items', [])
        task_status = request.data.get('task_status', None)
        saved = request.data.get('saved')

        with transaction.atomic():
            task_worker = TaskWorker.objects.get(worker=request.user.userprofile.worker, task=task)
            task_worker.task_status = task_status
            task_worker.save()

            task_worker_results = TaskWorkerResult.objects.filter(task_worker_id=task_worker.id)

            if task_status == TaskWorkerResult.STATUS_CREATED:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True, partial=True)
            else:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True)

            if serializer.is_valid():
                if task_worker_results.count() != 0:
                    serializer.update(task_worker_results, serializer.validated_data)
                else:
                    serializer.create(task_worker=task_worker)

                if task_status == TaskWorkerResult.STATUS_CREATED or saved:
                    return Response('Success', status.HTTP_200_OK)
                elif task_status == TaskWorkerResult.STATUS_ACCEPTED and not saved:

                    if not auto_accept:
                        serialized_data = {}
                        http_status = 204
                        return Response(serialized_data, http_status)

                    task_worker_serializer = TaskWorkerSerializer()
                    instance, http_status = task_worker_serializer.create(
                        worker=request.user.userprofile.worker, project=task_worker.task.project_id)
                    serialized_data = {}

                    if http_status == status.HTTP_200_OK:
                        serialized_data = TaskWorkerSerializer(instance=instance).data

                    return Response(serialized_data, http_status)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ExternalSubmit(APIView):
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
                if task_worker.task_status in [1, 2, 5]:
                    task_worker_result.status = 1
                    task_worker_result.result = request.data
                    task_worker_result.save()
                    return Response(request.data, status=status.HTTP_200_OK)
                else:
                    return Response("Task cannot be modified now", status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response("Invalid identifier", status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
