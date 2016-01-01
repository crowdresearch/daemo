from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

from crowdsourcing.serializers.task import *
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.models import Task, TaskWorker, TaskWorkerResult
from crowdsourcing.permissions.task import HasExceededReservedLimit
from crowdsourcing.serializers.rating import WorkerRequesterRatingSerializer


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

    def destroy(self, request, *args, **kwargs):
        task_serializer = TaskSerializer()
        task = self.get_object()
        task_serializer.delete(task)
        return Response({'status': 'deleted task'})

    @detail_route(methods=['get'])
    def retrieve_with_data(self, request, *args, **kwargs):
        task = self.get_object()
        task_worker = TaskWorker.objects.get(id=request.query_params['taskWorkerId'])
        serializer = TaskSerializer(instance=task,
                                    fields=('id', 'task_template', 'project_data', 'status', 'has_comments'))
        rating = models.WorkerRequesterRating.objects.filter(origin=request.user.userprofile.id,
                                                             target=task.project.owner.profile.id,
                                                             origin_type='worker', project=task.project.id)
        template = serializer.data.get('task_template', [])
        for item in template['template_items']:
            # unique ids to send back for additional layer of security
            if item['type'] == 'iframe':
                from django.conf import settings
                from hashids import Hashids
                hash = Hashids(salt=settings.SECRET_KEY)
                item['identifier'] = hash.encode(task_worker.id, task.id, item['id'])

        serializer.data['task_template'] = template

        requester_alias = task.project.owner.alias
        project = task.project.id
        target = task.project.owner.profile.id
        if rating.count() != 0:
            rating_serializer = WorkerRequesterRatingSerializer(instance=rating, many=True,
                                                                fields=('id', 'weight'))
            return Response({'data': serializer.data,
                             'rating': rating_serializer.data,
                             'requester_alias': requester_alias,
                             'project': project,
                             'target': target}, status.HTTP_200_OK)
        else:
            return Response({'data': serializer.data,
                             'requester_alias': requester_alias,
                             'project': project,
                             'target': target}, status.HTTP_200_OK)

    @list_route(methods=['get'])
    def list_by_project(self, request, **kwargs):
        tasks = Task.objects.filter(project=request.query_params.get('project_id'))
        task_serializer = TaskSerializer(instance=tasks, many=True, fields=('id', 'status',
                                                                            'template_items_monitoring',
                                                                            'task_workers_monitoring',
                                                                            'has_comments', 'comments'))
        response_data = {
            'project_name': tasks[0].project.name,
            'project_id': tasks[0].project.id,
            'project_description': tasks[0].project.description,
            'tasks': task_serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)

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
        serializer = TaskWorkerSerializer(data=request.data)
        if serializer.is_valid():
            instance, http_status = serializer.create(worker=request.user.userprofile.worker,
                                                      project=request.data.get('project', None))
            serialized_data = {}
            if http_status == status.HTTP_200_OK:
                serialized_data = TaskWorkerSerializer(instance=instance).data
            return Response(serialized_data, http_status)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        serializer = TaskWorkerSerializer()
        obj = self.queryset.get(task=kwargs['task__id'], worker=request.user.userprofile.worker.id)
        instance, http_status = serializer.create(worker=request.user.userprofile.worker, project=obj.task.project_id)
        obj.task_status = 6
        obj.save()
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
                                             fields=('id', 'task', 'task_status', 'task_worker_results_monitoring',
                                                     'worker_alias', 'updated_delta')).data, status.HTTP_200_OK)

    @list_route(methods=['get'])
    def list_by_status(self, request, *args, **kwargs):
        # Show all task types which are not skipped
        status_map = filter(lambda t: t[0] != TaskWorker.STATUS.skipped, TaskWorker.STATUS._triples)

        response = dict()
        for key, _, value in status_map:
            task_workers = TaskWorker.objects.filter(worker=request.user.userprofile.worker, task_status=key)
            serializer = TaskWorkerSerializer(instance=task_workers, many=True,
                                              fields=(
                                                  'id', 'task_status', 'task', 'requester_alias', 'project',
                                                  'is_paid', 'updated_delta'))
            response[value] = serializer.data
        return Response(response, status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def retrieve_with_data_and_results(self, request, *args, **kwargs):
        task_worker = TaskWorker.objects.get(id=request.query_params['id'])
        serializer = TaskWorkerSerializer(instance=task_worker,
                                          fields=('task', 'task_status', 'task_template', 'has_comments'))

        template = serializer.data.get('task_template', [])
        for item in template['template_items']:
            # unique ids to send back for additional layer of security
            if item['type'] == 'iframe':
                from django.conf import settings
                from hashids import Hashids
                hash = Hashids(salt=settings.SECRET_KEY)
                item['identifier'] = hash.encode(task_worker.id, task_worker.task.id, item['id'])

        rating = models.WorkerRequesterRating.objects.filter(origin=request.user.userprofile.id,
                                                             target=task_worker.task.project.owner.profile.id,
                                                             origin_type='worker', project=task_worker.task.project.id)
        requester_alias = task_worker.task.project.owner.alias
        project = task_worker.task.project.id
        target = task_worker.task.project.owner.profile.id
        if rating.count() != 0:
            rating_serializer = WorkerRequesterRatingSerializer(instance=rating, many=True,
                                                                fields=('id', 'weight'))
            return Response({'data': serializer.data,
                             'rating': rating_serializer.data,
                             'requester_alias': requester_alias,
                             'project': project,
                             'target': target}, status.HTTP_200_OK)
        else:
            return Response({'data': serializer.data,
                             'requester_alias': requester_alias,
                             'project': project,
                             'target': target}, status.HTTP_200_OK)

    @list_route(methods=['post'])
    def drop_saved_tasks(self, request, *args, **kwargs):
        task_ids = request.data.get('task_ids', [])
        self.queryset.filter(task_id__in=task_ids, worker=request.user.userprofile.worker.id).update(
            task_status=TaskWorker.STATUS.skipped, last_updated=timezone.now())
        return Response('Success', status.HTTP_200_OK)

    @list_route(methods=['post'])
    def bulk_pay_by_project(self, request, *args, **kwargs):
        project = request.data.get('project')
        accepted, rejected = 3, 4
        task_workers = TaskWorker.objects.filter(task__project=project).filter(
            Q(task_status=accepted) | Q(task_status=rejected))
        task_workers.update(is_paid=True, last_updated=timezone.now())
        return Response('Success', status.HTTP_200_OK)


class TaskWorkerResultViewSet(viewsets.ModelViewSet):
    queryset = TaskWorkerResult.objects.all()
    serializer_class = TaskWorkerResultSerializer

    # permission_classes = [IsOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        task_worker_result = self.queryset.filter(id=kwargs['pk'])[0]
        status = TaskWorkerResult.STATUS.created

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
        template_items = request.data.get('template_items', [])
        task_status = request.data.get('task_status', None)
        saved = request.data.get('saved')

        with transaction.atomic():
            task_worker = TaskWorker.objects.get(worker=request.user.userprofile.worker, task=task)
            task_worker.task_status = task_status
            task_worker.save()

            task_worker_results = TaskWorkerResult.objects.filter(task_worker_id=task_worker.id)

            if task_status == TaskWorkerResult.STATUS.created:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True, partial=True)
            else:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True)

            if serializer.is_valid():
                if task_worker_results.count() != 0:
                    serializer.update(task_worker_results, serializer.validated_data)
                else:
                    serializer.create(task_worker=task_worker)
                if task_status == TaskWorkerResult.STATUS.created or saved:
                    return Response('Success', status.HTTP_200_OK)
                elif task_status == TaskWorkerResult.STATUS.accepted and not saved:
                    task_worker_serializer = TaskWorkerSerializer()
                    instance, http_status = task_worker_serializer.create(
                        worker=request.user.userprofile.worker, project=task_worker.task.project_id)
                    serialized_data = {}

                    if http_status == status.HTTP_200_OK:
                        serialized_data = TaskWorkerSerializer(instance=instance).data

                    return Response(serialized_data, http_status)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class CurrencyViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Currency

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class ExternalSubmit(APIView):
    def post(self, request, *args, **kwargs):
        identifier = request.query_params.get('daemo_id', False)

        if not identifier:
            return Response("Missing identifier", status=status.HTTP_400_BAD_REQUEST)

        try:
            from django.conf import settings
            from hashids import Hashids
            hash = Hashids(salt=settings.SECRET_KEY)
            task_worker_id, task_id, template_item_id = hash.decode(identifier)

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
