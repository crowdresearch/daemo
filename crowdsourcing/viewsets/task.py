from crowdsourcing.serializers.task import *
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.shortcuts import get_object_or_404
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.models import Task, TaskWorker, TaskWorkerResult
from django.utils import timezone

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @detail_route(methods=['post'],permission_classes=[IsProjectOwnerOrCollaborator])
    def update_task(self, request, id=None):
        task_serializer = TaskSerializer(data=request.data)
        task = self.get_object()
        if task_serializer.is_valid():
            task_serializer.update(task,task_serializer.validated_data)
            return Response({'status': 'updated task'})
        else:
            return Response(task_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
  
    def list(self, request, *args, **kwargs):
        try:
            module = request.query_params.get('module')
            task = Task.objects.filter(module=module)
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
        serializer = TaskSerializer(instance=task, fields=('id', 'task_template', 'status'))
        return Response(serializer.data, status.HTTP_200_OK)

    @list_route(methods=['get'])
    def list_by_module(self, request, **kwargs):
        tasks = Task.objects.filter(module=request.query_params.get('module_id'))
        task_serializer = TaskSerializer(instance=tasks, many=True, fields=('id', 'status', \
                                        'template_items_monitoring', 'task_workers_monitoring'))
        response_data = {
            'project_name': tasks[0].module.project.name,
            'project_id': tasks[0].module.project.id,
            'module_name': tasks[0].module.name,
            'module_id': tasks[0].module.id,
            'tasks': task_serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)

class TaskWorkerViewSet(viewsets.ModelViewSet):
    queryset = TaskWorker.objects.all()
    serializer_class = TaskWorkerSerializer
    #permission_classes = [IsAuthenticated]
    lookup_field = 'task__id'

    def create(self, request, *args, **kwargs):
        serializer = TaskWorkerSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.create(worker=request.user.userprofile.worker, module=request.data.get('module', None))
            serialized_data = TaskWorkerSerializer(instance=instance)
            return Response(serialized_data.data, 200)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        serializer = TaskWorkerSerializer()
        obj = self.queryset.get(task=kwargs['task__id'], worker=request.user.userprofile.worker.id)
        obj.task_status = 6
        obj.save()
        instance = serializer.create(worker=request.user.userprofile.worker, module=obj.task.module_id)
        serialized_data = TaskWorkerSerializer(instance=instance)
        return Response(serialized_data.data, status.HTTP_200_OK)

    @list_route(methods=['post'])
    def bulk_update_status(self, request, *args, **kwargs):
        task_status = request.data.get('task_status', -1)
        task_workers = TaskWorker.objects.filter(id__in=tuple(request.data.get('task_workers', [])))
        task_workers.update(task_status=task_status, last_updated=timezone.now())
        return Response(TaskWorkerSerializer(instance=task_workers, many=True, 
                        fields=('id', 'task', 'task_status', 'task_worker_results_monitoring',
                                'worker_alias', 'updated_delta')).data, status.HTTP_200_OK)


class TaskWorkerResultViewSet(viewsets.ModelViewSet):
    queryset = TaskWorkerResult.objects.all()
    serializer_class = TaskWorkerResultSerializer
    #permission_classes = [IsOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        task_worker_result_serializer = TaskWorkerResultSerializer(data=request.data)
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
        task_worker = TaskWorker.objects.get(worker=request.user.userprofile.worker, task=task)
        serializer = TaskWorkerResultSerializer(data=template_items, many=True)
        if serializer.is_valid():
            serializer.create(task_worker=task_worker)
            task_worker_serializer = TaskWorkerSerializer()
            instance = task_worker_serializer.create(worker=request.user.userprofile.worker, module=task_worker.task.module_id)
            serialized_data = TaskWorkerSerializer(instance=instance)
            return Response(serialized_data.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class CurrencyViewSet(viewsets.ModelViewSet):
  from crowdsourcing.models import Currency
  queryset = Currency.objects.all()
  serializer_class = CurrencySerializer