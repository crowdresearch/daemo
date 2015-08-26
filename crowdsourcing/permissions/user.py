from rest_framework import permissions

class IsWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user.userprofile, 'worker')

class IsRequester(permissions.BasePermission):
    def has_object_permission(self, request, view, object):
        return hasattr(request.user.userprofile, 'requester')