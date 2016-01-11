from rest_framework import permissions


class IsProjectOwnerOrCollaborator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user.userprofile.requester:
            return True
        return False


class IsReviewerOrRaterOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.worker.profile.user == request.user
