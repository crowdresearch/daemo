from rest_framework import permissions


class IsTaskWorker(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.worker == request.user.userprofile.worker

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return True