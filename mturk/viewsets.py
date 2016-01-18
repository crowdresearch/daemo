from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from mturk.models import MTurkHIT, MTurkAssignment
from crowdsourcing.models import TaskWorker
from rest_framework.response import Response
from rest_framework import status
from crowdsourcing.serializers.task import TaskSerializer


class MTurkAssignmentViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = MTurkAssignment.objects.all()
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        task_id = request.data.get('task_id', -1)
        hit_id = request.data.get('hitId', -1)
        mturk_hit = get_object_or_404(MTurkHIT, task_id=task_id, hit_id=hit_id)
        assignment_id = request.data.get('assignmentId', -1)
        worker_id = request.data.get('workerId', -1)
        assignment, created = MTurkAssignment.objects.get_or_create(hit=mturk_hit,
                                                                    assignment_id=assignment_id, worker_id=worker_id)
        if created:
            assignment.status = TaskWorker.STATUS_IN_PROGRESS
            assignment.save()
        task_serializer = TaskSerializer(instance=assignment.hit.task,
                                         fields=('id', 'task_template', 'project_data', 'status'))
        return Response(data=task_serializer.data, status=status.HTTP_200_OK)
