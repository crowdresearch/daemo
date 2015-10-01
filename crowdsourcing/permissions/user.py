from rest_framework import permissions
from csp import settings
from rest_framework.exceptions import PermissionDenied


class IsWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user.userprofile, 'worker')


class IsRequester(permissions.BasePermission):
    def has_object_permission(self, request, view, object):
        return hasattr(request.user.userprofile, 'requester')


class CanCreateAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create' and not (request.user.is_staff or settings.REGISTRATION_ALLOWED):
            raise PermissionDenied(detail='Registration is closed.')
        return True
