__author__ = 'dmorina, asmita, megha'

from crowdsourcing.serializers.worker import *
from crowdsourcing.models import *
from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    @detail_route(methods=['post'])
    def update_skill(self, request, id = None):
        skill_serializer = SkillSerializer(data=request.data)
        skill = self.get_object()
        if skill_serializer.is_valid():
            skill_serializer.update(skill,skill_serializer.validated_data)
            return Response({'status': 'Updated Skills'})
        else:
            return Response(skill_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            skill = self.queryset
            skill_serializer = SkillSerializer(skill, many = True)
            return Response(skill_serializer.data)
        except:
            return Response([])

    def destroy(self, request, *args, **kwargs):
        skill_serializer = SkillSerializer()
        skill = self.get_object()
        skill_serializer.delete(skill)
        return Response({'Status': 'Deleted Skills'})


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def update_worker(self, request, pk=None):
        worker_serializer = WorkerSkill(data=request.data)
        worker = self.get_object()
        if worker_serializer.is_valid():
            worker_serializer.update(worker,worker_serializer.validated_data)
            return Response({'status': 'Updated Worker'})
        else:
            return Response(worker_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            worker = Worker.objects.all()
            worker_serializer = WorkerSkill(worker, many=True)
            return Response(worker_serializer.data)
        except:
            return Response([])

    def destroy(self, request, *args, **kwargs):
        worker_serializer = WorkerSerializer()
        worker = self.get_object()
        worker_serializer.delete(worker)
        return Response({'status': 'Deleted Worker'})


class WorkerSkillViewSet(viewsets.ModelViewSet):
    queryset = WorkerSkill.objects.all()
    serializer_class = WorkerSkillSerializer

    def retrieve(self, request, *args, **kwargs):
        worker = get_object_or_404(self.queryset, worker=request.worker)
        serializer = WorkerSkillSerializer(instance=worker)
        return Response(serializer.data)


class TaskWorkerViewSet(viewsets.ModelViewSet):
    queryset = TaskWorker.objects.all()
    serializer_class = TaskWorkerSerializer

    def retrieve(self, request, *args, **kwargs):
        worker = get_object_or_404(self.queryset, worker=request.worker)
        serializer = TaskWorkerSerializer(instance=worker)
        return Response(serializer.data)


class TaskWorkerResultViewSet(viewsets.ModelViewSet):
    queryset = TaskWorkerResult.objects.all()
    serializer_class = TaskWorkerResultSerializer

    def retrieve(self, request, *args, **kwargs):
        worker = get_object_or_404(self.queryset, worker=request.worker)
        serializer = TaskWorkerResultSerializer(instance=worker)
        return Response(serializer.data)


class WorkerModuleApplicationViewSet(viewsets.ModelViewSet):
    queryset = WorkerModuleApplication.objects.all()
    serializer_class = WorkerModuleApplicationSerializer

    def retrieve(self, request, *args, **kwargs):
        worker = get_object_or_404(self.queryset, worker=request.worker)
        serializer = WorkerModuleApplicationSerializer(instance=worker)
        return Response(serializer.data)