__author__ = ['dmorina', 'asmita', 'megha']

from crowdsourcing.serializers.worker import *
from rest_framework import viewsets

class WorkerSkillViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import WorkerSkill
    queryset = WorkerSkill.objects.all()
    serializer_class = WorkerSkillSerializer
    

class WorkerViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Worker
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    

class SkillViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Skill
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    

class TaskWorkerViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TaskWorker
    queryset = TaskWorker.objects.all()
    serializer_class = TaskWorkerSerializer


class TaskWorkerResultViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TaskWorkerResult
    queryset = TaskWorkerResult.objects.all()
    serializer_class = TaskWorkerResultSerializer


class WorkerModuleApplicationViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import WorkerModuleApplication
    queryset = WorkerModuleApplication.objects.all()
    serializer_class = WorkerModuleApplicationSerializer



