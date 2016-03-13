from rest_framework import permissions
from crowdsourcing.models import Project


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


class IsProjectAvailable(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        query = '''
                WITH project_table AS
                    (SELECT project_id FROM crowdsourcing_task WHERE id = %(task_id)s),
                rating_table AS
                    (SELECT owner_id, min_rating FROM get_min_project_ratings()
                            WHERE project_id = (SELECT project_id FROM project_table))
                SELECT requester_id as id FROM get_worker_ratings(%(worker_profile)s)
                    WHERE requester_id = (select owner_id from rating_table)
                        AND worker_rating > (select min_rating from rating_table);
                '''

        task_id = obj.id
        resp = Project.objects.raw(query, params={'worker_profile': request.user.userprofile.id, 'task_id': task_id})
        return len(list(resp)) > 0
