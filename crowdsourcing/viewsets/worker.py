__author__ = ['dmorina', 'megha']

from crowdsourcing.serializers.worker import *
from rest_framework import status, views as rest_framework_views, viewsets
from crowdsourcing.models import Worker, Skill, WorkerSkill, TaskWorker, TaskWorkerResult, WorkerModuleApplication

class WorkerViewset(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

class SkillViewset(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class WorkerSkillViewset(viewsets.ModelViewSet):
    queryset = WorkerSkill.objects.all()
    serializer_class = WorkerSkillSerializer

class TaskWorkerViewset(viewsets.ModelViewSet):
    queryset = TaskWorker.objects.all()
    serializer_class = TaskWorkerSerializer

class TaskWorkerResultViewset(viewsets.ModelViewSet):
    queryset = TaskWorkerResult.objects.all()
    serializer_class = TaskWorkerResultSerializer

class WorkerModuleApplicationViewset(viewsets.ModelViewSet):
    queryset = WorkerModuleApplication.objects.all()
    serializer_class = WorkerModuleApplicationSerializer