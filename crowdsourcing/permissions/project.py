from rest_framework import permissions


class IsProjectOwnerOrCollaborator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user or request.user.is_superuser:
            return True
        return False


class ProjectChangesAllowed(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if view.action == 'update' and obj.status != obj.STATUS_DRAFT:
            return False
        return True
