from rest_framework import permissions
from crowdsourcing.models import TaskWorker
from rest_framework.exceptions import PermissionDenied

class HasExceededReservedLimit(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == 'create' and TaskWorker.objects.filter(worker=request.user.userprofile.worker,
                                                                 task_status__in=[1, 5]).count() >= 8:
            raise PermissionDenied(detail='You have exceeded maximum number of tasks in progress.')
        return True
