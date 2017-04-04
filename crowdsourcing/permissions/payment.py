from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.customer is None:
            return False
        return obj.customer.owner == request.user
