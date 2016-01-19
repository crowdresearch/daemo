from rest_framework import permissions


class IsValidHITAssignment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.worker_id == request.data.get('worker_id', -1) and \
                obj.assignment_id == request.data.get('assignment_id', -1) and \
                obj.hit_id == request.data.get('hit_id', -1):
            return True
        return False
