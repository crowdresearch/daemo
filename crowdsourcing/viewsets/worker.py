from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from crowdsourcing.serializers.worker import *
from crowdsourcing.serializers.project import *
from crowdsourcing.models import *
from crowdsourcing.permissions.util import *
from crowdsourcing.permissions.user import IsWorker


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @detail_route(methods=['post'])
    def update_skill(self, request, id=None):
        skill_serializer = SkillSerializer(data=request.data)
        skill = self.get_object()
        if skill_serializer.is_valid():
            skill_serializer.update(skill, skill_serializer.validated_data)
            return Response({'status': 'Updated Skills'})
        else:
            return Response(skill_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            skill = self.queryset
            skill_serializer = SkillSerializer(skill, many=True)
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
            worker_serializer.update(worker, worker_serializer.validated_data)
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

    @detail_route(methods=['GET'])
    def portfolio(self, request, *args, **kwargs):
        worker = self.get_object()
        projects = Project.objects.all().filter(deleted=False, status=4, task__taskworker__worker=worker).distinct()
        serializer = ProjectSerializer(instance=projects, many=True, fields=('id', 'name', 'categories',
                                                                           'num_reviews', 'completed_on', 'num_raters',
                                                                           'total_tasks', 'average_time'))
        return Response(serializer.data)

    def retrieve(self, request, profile__user__username=None):
        worker = get_object_or_404(self.queryset, profile__user__username=profile__user__username)
        serializer = self.serializer_class(worker)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='list-using-daemo-id')
    def list_using_daemo_id(self, request, *args, **kwargs):
        daemo_id = request.query_params.get('daemo_id', False)
        if not daemo_id:
            return Response("Missing daemo_id", status=status.HTTP_400_BAD_REQUEST)
        from django.conf import settings
        from hashids import Hashids
        identifier_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
        if len(identifier_hash.decode(daemo_id)) == 0:
            return Response("Invalid daemo_id", status=status.HTTP_400_BAD_REQUEST)
        task_worker_id, task_id, template_item_id = identifier_hash.decode(daemo_id)
        worker = TaskWorker.objects.filter(pk=task_worker_id).first().worker
        response_data = WorkerSerializer(instance=worker, fields=('id', 'alias')).data
        response_data.update({'daemo_id': daemo_id})
        return Response(data=response_data, status=status.HTTP_200_OK)


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
        worker_skill = get_object_or_404(self.queryset,
                                         worker=request.user.userprofile.worker, skill=kwargs['pk'])
        worker_skill.delete()
        return Response({'status': 'Deleted WorkerSkill'})
