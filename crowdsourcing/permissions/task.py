from django.conf import settings
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from crowdsourcing.models import TaskWorker, Task


class HasExceededReservedLimit(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create' \
            and TaskWorker.objects.filter(worker=request.user.id,
                                          status__in=[TaskWorker.STATUS_IN_PROGRESS,
                                                      TaskWorker.STATUS_RETURNED]
                                          ).count() >= settings.MAX_TASKS_IN_PROGRESS:
            raise PermissionDenied(detail='You have exceeded maximum number of tasks in progress.')
        return True


class IsTaskOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        task_id = request.data.get('task_id')
        task = Task.objects.prefetch_related('project__owner').filter(id=task_id).first()
        if task is None:
            return True
        return task.project.owner == request.user
