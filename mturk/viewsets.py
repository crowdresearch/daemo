from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from hashids import Hashids

from mturk.models import MTurkHIT, MTurkAssignment
from crowdsourcing.models import TaskWorker
from crowdsourcing.serializers.task import TaskSerializer
from mturk.interface import MTurkProvider
from csp import settings


class MTurkAssignmentViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = MTurkAssignment.objects.all()
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        provider = MTurkProvider('https://localhost:8000')
        task_id = request.data.get('taskId', -1)
        task_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.MTURK_HASH_MIN_LENGTH)
        task_id = task_hash.decode(task_id)
        if len(task_id) == 0:
            task_id = -1
        hit_id = request.data.get('hitId', -1)
        mturk_hit = get_object_or_404(MTurkHIT, task_id=task_id, hit_id=hit_id)
        assignment_id = request.data.get('assignmentId', -1)

        if assignment_id != 'ASSIGNMENT_ID_NOT_AVAILABLE':
            assignment, is_valid = provider.get_assignment(assignment_id)
            if not assignment or (is_valid and assignment.HITId != hit_id):
                return Response(data={"message": "Invalid assignment"}, status=status.HTTP_400_BAD_REQUEST)
            worker_id = request.data.get('workerId', -1)
            assignment, created = MTurkAssignment.objects.get_or_create(hit=mturk_hit,
                                                                        assignment_id=assignment_id,
                                                                        worker_id=worker_id)
            if created:
                assignment.status = TaskWorker.STATUS_IN_PROGRESS
                assignment.save()
        task_serializer = TaskSerializer(instance=mturk_hit.task,
                                         fields=('id', 'task_template', 'project_data', 'status'))
        return Response(data=task_serializer.data, status=status.HTTP_200_OK)
