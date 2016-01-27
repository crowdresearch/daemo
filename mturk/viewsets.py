from django.db import transaction
from django.shortcuts import get_object_or_404
from hashids import Hashids
from rest_framework import mixins, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from crowdsourcing.models import TaskWorker, TaskWorkerResult
from crowdsourcing.serializers.task import (TaskSerializer,
                                            TaskWorkerResultSerializer)
from csp import settings
from mturk.interface import MTurkProvider
from mturk.models import MTurkAssignment, MTurkHIT, MTurkNotification
from mturk.permissions import IsValidHITAssignment
from mturk.utils import get_or_create_worker


class MTurkAssignmentViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = MTurkAssignment.objects.all()
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        worker = get_or_create_worker(worker_id=request.data.get('workerId'))
        provider = MTurkProvider('https://' + request.get_host())
        task_id = request.data.get('taskId', -1)
        task_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.MTURK_HASH_MIN_LENGTH)
        task_id = task_hash.decode(task_id)
        if len(task_id) == 0:
            task_id = -1
        hit_id = request.data.get('hitId', -1)
        mturk_hit = get_object_or_404(MTurkHIT, task_id=task_id, hit_id=hit_id)
        assignment_id = request.data.get('assignmentId', -1)
        mturk_assignment_id = None
        if assignment_id != 'ASSIGNMENT_ID_NOT_AVAILABLE':
            assignment, is_valid = provider.get_assignment(assignment_id)
            if not assignment or (is_valid and assignment.HITId != hit_id):
                return Response(data={"message": "Invalid assignment"}, status=status.HTTP_400_BAD_REQUEST)
            task_worker, created = TaskWorker.objects.get_or_create(worker=worker, task_id=task_id[0])
            if created:
                task_worker.task_status = TaskWorker.STATUS_IN_PROGRESS
                task_worker.save()
            assignment, created = MTurkAssignment.objects.get_or_create(hit=mturk_hit,
                                                                        assignment_id=assignment_id,
                                                                        task_worker=task_worker)
            mturk_assignment_id = assignment.id
            if created:
                assignment.status = TaskWorker.STATUS_IN_PROGRESS
                assignment.save()
        task_serializer = TaskSerializer(instance=mturk_hit.task,
                                         fields=('id', 'template', 'project_data', 'status'))
        response_data = {
            'task': task_serializer.data,
            'assignment': mturk_assignment_id
        }
        return Response(data=response_data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], permission_classes=[IsValidHITAssignment], url_path='submit-results')
    def submit_results(self, request, *args, **kwargs):
        mturk_assignment = self.get_object()
        template_items = request.data.get('template_items', [])
        with transaction.atomic():
            task_worker_results = TaskWorkerResult.objects.filter(task_worker_id=mturk_assignment.task_worker.id)
            serializer = TaskWorkerResultSerializer(data=template_items, many=True)
            if serializer.is_valid():
                if task_worker_results.count() != 0:
                    serializer.update(task_worker_results, serializer.validated_data)
                else:
                    serializer.create(task_worker=mturk_assignment.task_worker)
                mturk_assignment.task_worker.task_status = TaskWorker.STATUS_SUBMITTED
                mturk_assignment.task_worker.save()
                return Response(data={'message': 'Success'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post', 'get'], url_path='notification')
    def notification(self, request, *args, **kwargs):
        hit_id = request.query_params.get('Event.1.HITId')
        assignment_id = request.query_params.get('Event.1.AssignmentId')
        event_type = request.query_params.get('Event.1.EventType')
        mturk_assignment = MTurkAssignment.objects.filter(hit__hit_id=hit_id, assignment_id=assignment_id).first()
        if event_type in ['AssignmentReturned', 'AssignmentAbandoned']:
            mturk_assignment.status = TaskWorker.STATUS_SKIPPED
            mturk_assignment.task_worker.task_status = TaskWorker.STATUS_SKIPPED
            mturk_assignment.task_worker.save()
            mturk_assignment.save()
        MTurkNotification.objects.create(data=request.query_params)
        return Response(data={}, status=status.HTTP_200_OK)
