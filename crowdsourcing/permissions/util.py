from rest_framework import permissions
from django.conf import settings


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsSandbox(permissions.BasePermission):
    def has_permission(self, request, view):
        host = request.get_host()
        return host not in settings.PRODUCTION_HOSTS
