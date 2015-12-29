from crowdsourcing.serializers.task import *
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.shortcuts import get_object_or_404
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.models import Task, TaskWorker, TaskWorkerResult
from django.utils import timezone
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
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
        serializer = TaskSerializer(instance=task,
                                    fields=('id', 'template', 'project_data', 'status', 'has_comments'))
        rating = models.WorkerRequesterRating.objects.filter(origin=request.user.userprofile.id,
                                                             target=task.project.owner.profile.id,
                                                             origin_type='worker', project=task.project.id)

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
        serializer = TaskWorkerSerializer(data=request.data)
        if serializer.is_valid():
            instance, http_status = serializer.create(worker=request.user.userprofile.worker,
                                                      project=request.data.get('project', None))
            serialized_data = {}
            if http_status == 200:
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
        if http_status == 200:
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

    @detail_route(methods=['post'], url_path='accept-all')
    def accept_all(self, request, *args, **kwargs):
        from itertools import chain
        task_workers = TaskWorker.objects.filter(task_status=2, task_id=kwargs['task__id'])
        list_workers = list(chain.from_iterable(task_workers.values_list('id')))
        task_workers.update(task_status=3, last_updated=timezone.now())
        return Response(data=list_workers, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def list_by_status(self, request, *args, **kwargs):
        status_map = {1: 'In Progress', 2: 'Submitted', 3: 'Accepted', 4: 'Rejected', 5: 'Returned'}
        response = dict()
        for key, value in status_map.iteritems():
            task_workers = TaskWorker.objects.filter(worker=request.user.userprofile.worker, task_status=key)
            serializer = TaskWorkerSerializer(instance=task_workers, many=True,
                                              fields=(
                                                  'id', 'task_status', 'task', 'requester_alias', 'project',
                                                  'is_paid', 'last_updated'))
            response[value] = serializer.data
        return Response(response, status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def retrieve_with_data_and_results(self, request, *args, **kwargs):
        task_worker = TaskWorker.objects.get(id=request.query_params['id'])
        serializer = TaskWorkerSerializer(instance=task_worker,
                                          fields=('task', 'task_status', 'task_template', 'has_comments'))
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
            task_status=6, last_updated=timezone.now())
        return Response('Success', status.HTTP_200_OK)

    @list_route(methods=['post'])
    def bulk_pay_by_project(self, request, *args, **kwargs):
        project = request.data.get('project')
        accepted, rejected = 3, 4
        task_workers = TaskWorker.objects.filter(task__project=project).filter(
            Q(task_status=accepted) | Q(task_status=rejected))
        task_workers.update(is_paid=True, last_updated=timezone.now())
        return Response('Success', status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path="list-submissions")
    def list_submissions(self, request, *args, **kwargs):
        workers = TaskWorker.objects.filter(task_status__in=[2, 3, 5], task_id=kwargs.get('task__id', -1))
        serializer = TaskWorkerSerializer(instance=workers, many=True,
                                          fields=('id', 'task_worker_results',
                                                  'worker_alias', 'worker', 'task_status'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class TaskWorkerResultViewSet(viewsets.ModelViewSet):
    queryset = TaskWorkerResult.objects.all()
    serializer_class = TaskWorkerResultSerializer

    # permission_classes = [IsOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        task_worker_result = self.queryset.filter(id=kwargs['pk'])[0]
        status = 1
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
            if task_status == 1:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True, partial=True)
            else:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True)
            if serializer.is_valid():
                if task_worker_results.count() != 0:
                    serializer.update(task_worker_results, serializer.validated_data)
                else:
                    serializer.create(task_worker=task_worker)
                if task_status == 1 or saved:
                    return Response('Success', status.HTTP_200_OK)
                elif task_status == 2 and not saved:
                    task_worker_serializer = TaskWorkerSerializer()
                    instance, http_status = task_worker_serializer.create(
                        worker=request.user.userprofile.worker, project=task_worker.task.project_id)
                    serialized_data = {}
                    if http_status == 200:
                        serialized_data = TaskWorkerSerializer(instance=instance).data
                    return Response(serialized_data, http_status)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class CurrencyViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Currency

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
