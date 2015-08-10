__author__ = 'dmorina, asmita, megha'

from crowdsourcing.serializers.worker import *
from crowdsourcing.serializers.project import *
from crowdsourcing.models import *
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from crowdsourcing.permissions.util import *
from crowdsourcing.permissions.user import IsWorker


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsOwnerOrReadOnly]

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
    lookup_value_regex = '[^/]+'
    lookup_field = 'profile__user__username'
    # permission_classes = [IsOwnerOrReadOnly]

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def update_worker(self, request, pk=None):
        worker_serializer = WorkerSerializer(data=request.data)
        worker = self.get_object()
        if worker_serializer.is_valid():
            worker_serializer.update(worker,worker_serializer.validated_data)
            return Response({'status': 'Updated Worker'})
        else:
            return Response(worker_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            worker = Worker.objects.all()
            worker_serializer = WorkerSerializer(worker, many=True)
            return Response(worker_serializer.data)
        except:
            return Response([])

    def destroy(self, request, *args, **kwargs):
        worker_serializer = WorkerSerializer()
        worker = self.get_object()
        worker_serializer.delete(worker)
        return Response({'status': 'Deleted Worker'})

    @detail_route(methods = ['GET'])
    def portfolio(self, request, *args, **kwargs):
        worker = self.get_object()
        modules = Module.objects.all().filter(deleted=False,status=4,task__taskworker__worker = worker).distinct()
        serializer = ModuleSerializer(instance = modules,many = True,fields = ('id', 'name', 'project', 'categories',
             'num_reviews','completed_on','num_raters','total_tasks','average_time'))
        return Response(serializer.data)

    def retrieve(self, request, profile__user__username=None):
        worker = get_object_or_404(self.queryset, profile__user__username=profile__user__username)
        serializer = self.serializer_class(worker)
        return Response(serializer.data)


class WorkerSkillViewSet(viewsets.ModelViewSet):
    queryset = WorkerSkill.objects.all()
    serializer_class = WorkerSkillSerializer
    permission_classes = [IsAuthenticated, IsWorker]

    def retrieve(self, request, *args, **kwargs):
        worker = get_object_or_404(self.queryset, worker=request.worker)
        serializer = WorkerSkillSerializer(instance=worker)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = WorkerSkillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(worker=request.user.userprofile.worker)
            return Response({'status': 'Worker skill created'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        workerskill_serializer = WorkerSkillSerializer()
        worker_skill = get_object_or_404(self.queryset,
            worker=request.user.userprofile.worker, skill=kwargs['pk'])
        worker_skill.delete()
        return Response({'status': 'Deleted WorkerSkill'})


class WorkerModuleApplicationViewSet(viewsets.ModelViewSet):
    queryset = WorkerModuleApplication.objects.all()
    serializer_class = WorkerModuleApplicationSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        worker = get_object_or_404(self.queryset, worker=request.worker)
        serializer = WorkerModuleApplicationSerializer(instance=worker)
        return Response(serializer.data)
