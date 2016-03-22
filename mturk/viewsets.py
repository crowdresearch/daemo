from django.db import transaction
from django.shortcuts import get_object_or_404
from hashids import Hashids
from rest_framework import mixins, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from crowdsourcing.models import TaskWorker, TaskWorkerResult
from crowdsourcing.serializers.task import (TaskSerializer,
                                            TaskWorkerResultSerializer)
from csp import settings
from mturk.models import MTurkAssignment, MTurkHIT, MTurkNotification, MTurkAccount
from mturk.permissions import IsValidHITAssignment
from mturk.serializers import MTurkAccountSerializer
from mturk.tasks import mturk_hit_update, get_provider
from mturk.utils import get_or_create_worker


class MTurkAssignmentViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = MTurkAssignment.objects.all()
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        worker = get_or_create_worker(worker_id=request.data.get('workerId'))
        task_id = request.data.get('taskId', -1)
        task_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
        task_id = task_hash.decode(task_id)
        if len(task_id) == 0:
            task_id = -1
        hit_id = request.data.get('hitId', -1)
        mturk_hit = get_object_or_404(MTurkHIT, task_id=task_id, hit_id=hit_id)
        assignment_id = request.data.get('assignmentId', -1)
        mturk_assignment_id = None
        task_worker = None
        provider = get_provider(mturk_hit.task.project.owner.profile.user, host='https://' + request.get_host())

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
                                         fields=('id', 'template', 'project_data', 'status'),
                                         context={'task_worker': task_worker})
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
                mturk_assignment.status = TaskWorker.STATUS_SUBMITTED
                mturk_assignment.save()
                if str(settings.MTURK_ONLY) == 'True':
                    pass
                else:
                    mturk_hit_update.delay({'id': mturk_assignment.task_worker.task_id})
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


class MTurkConfig(ViewSet):

    @staticmethod
    def get_mturk_url(request):
        host = settings.MTURK_WORKER_HOST
        return Response({'url': host}, status=status.HTTP_200_OK)


class MTurkAccountViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = MTurkAccount.objects.all()
    serializer_class = MTurkAccountSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                account = serializer.create(user=request.user)
                return Response(data=self.serializer_class(instance=account).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'mturk_account'):
            return Response(data={}, status=status.HTTP_204_NO_CONTENT)
        obj = self.request.user.mturk_account
        serializer = self.serializer_class(instance=obj)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['delete'])
    def remove(self, request, *args, **kwargs):
        request.user.mturk_account.delete()
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)
