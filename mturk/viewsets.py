from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import detail_route, list_route
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from hashids import Hashids
from django.db import transaction
from mturk.models import MTurkHIT, MTurkAssignment, MTurkNotification
from crowdsourcing.models import TaskWorker, TaskWorkerResult
from crowdsourcing.serializers.task import TaskSerializer, TaskWorkerResultSerializer
from mturk.interface import MTurkProvider
from mturk.permissions import IsValidHITAssignment
from csp import settings


class MTurkAssignmentViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = MTurkAssignment.objects.all()
    serializer_class = TaskSerializer
    mturk_user = None

    def create(self, request, *args, **kwargs):
        self.mturk_user = User.objects.get(username=settings.MTURK_WORKER_USERNAME)
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
            worker_id = request.data.get('workerId', -1)
            assignment, created = MTurkAssignment.objects.get_or_create(hit=mturk_hit,
                                                                        assignment_id=assignment_id,
                                                                        worker_id=worker_id)
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
        self.mturk_user = User.objects.get(username=settings.MTURK_WORKER_USERNAME)
        mturk_assignment = self.get_object()
        template_items = request.data.get('template_items', [])
        with transaction.atomic():
            if not mturk_assignment.task_worker:
                task_worker, created = TaskWorker.objects.get_or_create(worker=self.mturk_user.userprofile.worker,
                                                                        task=mturk_assignment.hit.task,
                                                                        task_status=TaskWorker.STATUS_SUBMITTED)
                mturk_assignment.task_worker = task_worker
                mturk_assignment.save()
            task_worker_results = TaskWorkerResult.objects.filter(task_worker_id=mturk_assignment.task_worker.id)
            serializer = TaskWorkerResultSerializer(data=template_items, many=True)
            if serializer.is_valid():
                if task_worker_results.count() != 0:
                    serializer.update(task_worker_results, serializer.validated_data)
                else:
                    serializer.create(task_worker=mturk_assignment.task_worker)
                return Response(data={'message': 'Success'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post', 'get'], url_path='notification')
    def notification(self, request, *args, **kwargs):
        MTurkNotification.objects.create(data={'id': 1})
        MTurkNotification.objects.create(data=request.data)
        MTurkNotification.objects.create(data=request.query_params)
        return Response(data={}, status=status.HTTP_200_OK)
