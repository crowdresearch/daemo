from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from crowdsourcing.models import TaskWorker


class HasExceededReservedLimit(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create' and TaskWorker.objects.filter(worker=request.user.userprofile.worker,
                                                                 task_status__in=[1, 5]).count() >= 8:
            raise PermissionDenied(detail='You have exceeded maximum number of tasks in progress.')
        return True


class AlreadyAssigned(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if view.action == 'assign' and obj.reviewer is not None and obj.reviewer != request.user.userprofile.worker:
            raise PermissionDenied(detail='This task is already assigned to someone and is in progress.')
        return True
