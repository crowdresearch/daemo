__author__ = 'elsabakiu, dmorina, asmita, megha,kajal'

from crowdsourcing.serializers.task import *
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.shortcuts import get_object_or_404
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.models import Task, TaskWorker, TaskWorkerResult

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


class TaskWorkerViewSet(viewsets.ModelViewSet):
    queryset = TaskWorker.objects.all()
    serializer_class = TaskWorkerSerializer
    #permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = TaskWorkerSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.create(worker=request.user.userprofile.worker)
            serialized_data = TaskWorkerSerializer(instance=instance)
            return Response(serialized_data.data, 200)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


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


class CurrencyViewSet(viewsets.ModelViewSet):
  from crowdsourcing.models import Currency
  queryset = Currency.objects.all()
  serializer_class = CurrencySerializer