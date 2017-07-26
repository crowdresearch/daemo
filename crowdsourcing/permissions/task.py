from django.conf import settings
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from crowdsourcing.models import Project
from django.db import connection

from crowdsourcing.models import TaskWorker, Task


class HasExceededReservedLimit(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create' \
            and TaskWorker.objects.filter(worker=request.user.id,
                                          status__in=[TaskWorker.STATUS_IN_PROGRESS,
                                                      TaskWorker.STATUS_RETURNED]
                                          ).count() >= settings.MAX_TASKS_IN_PROGRESS:
            raise PermissionDenied(detail='You have exceeded maximum number of tasks in progress.')
        return True


class IsTaskOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        task_id = request.data.get('task_id')
        task = Task.objects.prefetch_related('project__owner').filter(id=task_id).first()
        if task is None:
            return True
        return task.project.owner == request.user


class IsQualified(permissions.BasePermission):
    # noinspection SqlResolve
    def has_permission(self, request, view):
        if view.action == 'create':
            project_id = request.data.get('project', None)
            if project_id is None:
                return False
            project = Project.objects.values('id', 'min_rating', 'owner_id').get(id=project_id)
            cursor = connection.cursor()
            query = '''
                select * from get_worker_ratings(%(worker_id)s) 
                where requester_id=%(owner_id)s;
            '''
            cursor.execute(query, {'worker_id': request.user.id, 'owner_id': project['owner_id']})
            rating = cursor.fetchall()
            cursor.close()
            avg_rating = rating[0][1] or 1.99
            if avg_rating < project['min_rating']:
                raise PermissionDenied(detail='You don\'t have permission to access this project.')
        return True
