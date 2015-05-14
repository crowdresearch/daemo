__author__ = 'dmorina'
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsProjectCollaborator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        for collaborator in obj.collaborators.all():
            if collaborator.profile.user==request.user:
                return True

        return False
