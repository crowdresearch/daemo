__author__ = 'elsabakiu, dmorina, asmita, megha,kajal'

from crowdsourcing.serializers.task import *
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.models import Worker,TaskWorker,Module
from django.shortcuts import get_object_or_404
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.models import Task
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
    
class CurrencyViewSet(viewsets.ModelViewSet):
  from crowdsourcing.models import Currency
  queryset = Currency.objects.all()
  serializer_class = CurrencySerializer