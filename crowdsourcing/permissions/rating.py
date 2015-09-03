from rest_framework import permissions


class IsRatingOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if view.action in ('update', 'destroy',):
            return obj.origin == request.user.userprofile
        return True
