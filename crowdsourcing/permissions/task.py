from rest_framework import permissions
from crowdsourcing.models import TaskWorker

class HasExceededReservedLimit(permissions.BasePermission):
    message = 'You have exceeded maximum number of tasks in progress.'

    def has_permission(self, request, view):
        if view.action == 'create':
            return TaskWorker.objects.filter(worker=request.user.userprofile.worker, task_status__in=[1, 5]).count() < 9
