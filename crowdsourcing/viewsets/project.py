from rest_framework import status, viewsets
from rest_framework.response import Response
from crowdsourcing.serializers.project import *
from crowdsourcing.serializers.task import TaskWorkerSerializer
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.models import Module, Category, Project, Requester, ProjectRequester, \
    ModuleReview, ModuleRating, BookmarkedProjects, Task, TaskWorker, WorkerRequesterRating, Worker
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.permissions.util import IsOwnerOrReadOnly
from crowdsourcing.permissions.project import IsReviewerOrRaterOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from crowdsourcing.utils import get_model_or_none


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(deleted=False)
    serializer_class = CategorySerializer

    @detail_route(methods=['post'])
    def update_category(self, request, id=None):
        category_serializer = CategorySerializer(data=request.data)
        category = self.get_object()
        if category_serializer.is_valid():
            category_serializer.update(category, category_serializer.validated_data)

            return Response({'status': 'updated category'})
        else:
            return Response(category_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            category = self.queryset
            categories_serialized = CategorySerializer(category, many=True)
            return Response(categories_serialized.data)
        except:
            return Response([])

    def destroy(self, request, *args, **kwargs):
        category_serializer = CategorySerializer()
        category = self.get_object()
        category_serializer.delete(category)
        return Response({'status': 'deleted category'})


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.filter(deleted=False)
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    @detail_route(methods=['post'], permission_classes=[IsProjectOwnerOrCollaborator])
    def update_project(self, request, pk=None):
        project_serializer = ProjectSerializer(data=request.data, partial=True)
        project = self.get_object()
        if project_serializer.is_valid():
            project_serializer.update(project, project_serializer.validated_data)

            return Response({'status': 'updated project'})
        else:
            return Response(project_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        requester_id = -1
        if hasattr(request.user.userprofile, 'requester'):
            requester_id = request.user.userprofile.requester.id

        try:
            query = '''
                SELECT p.id, p.name, p.description, MAX(boomeranged_modules.imputed_wr_rating)
                    FROM (
                        SELECT id, name, description, owner_id, project_id, imputed_min_rating,
                            CASE WHEN wr_weight IS NULL AND avg_wr_rating IS NOT NULL THEN avg_wr_rating
                            WHEN wr_weight IS NULL AND avg_wr_rating IS NULL THEN 1.99
                            WHEN wr_weight IS NOT NULL AND avg_wr_rating IS NULL THEN wr_weight
                            ELSE wr_weight + 0.1 * avg_wr_rating END imputed_wr_rating
                        FROM (
                            SELECT cascade_cond.*, wr_rating.weight as wr_weight, avg_wr_rating.avg_wr_rating
                            FROM (
                                SELECT cascade_agg.*
                                FROM(
                                    SELECT cascade_all.*,
                                        CASE WHEN weight IS NULL
                                        AND adj_avg_rw_rating IS NOT NULL THEN adj_avg_rw_rating
                                        WHEN weight IS NULL AND adj_avg_rw_rating IS NULL THEN 1.99
                                        WHEN weight IS NOT NULL AND adj_avg_rw_rating IS NULL THEN weight
                                        ELSE weight + 0.1 * adj_avg_rw_rating END imputed_rw_rating
                                    FROM (
                                        SELECT m.id, m.project_id, m.owner_id, m.name, m.description, 
                                            rw_rating.weight, rw_rating.adj_avg_rw_rating, imputed_min_rating
                                        FROM crowdsourcing_module m
                                        INNER JOIN crowdsourcing_requester r ON m.owner_id = r.id
                                        INNER JOIN crowdsourcing_userprofile u ON r.profile_id = u.id
                                        LEFT OUTER JOIN (
                                            SELECT wrr.origin_id, wrr.target_id
                                            FROM crowdsourcing_workerrequesterrating wrr
                                            INNER JOIN (
                                                SELECT origin_id, MAX(last_updated) AS max_date
                                                FROM crowdsourcing_workerrequesterrating
                                                WHERE origin_type='requester' AND target_id = %(worker_profile)s
                                                GROUP BY origin_id
                                            ) most_recent
                                            ON wrr.origin_id = most_recent.origin_id AND wrr.target_id = %(worker_profile)s
                                            AND wrr.last_updated = most_recent.max_date AND wrr.origin_type='requester' 
                                        ) recent_req_rating
                                        ON u.id = recent_req_rating.origin_id
                                        LEFT OUTER JOIN (
                                            SELECT avg_rw_rating.origin_id, avg_rw_rating.target_id, avg_rw_rating.avg_rw_rating, avg_rw_rating.count,
                                                avg_rw_rating.weight, 
                          CASE WHEN avg_rw_rating.count=1 THEN avg_rw_rating.avg_rw_rating
                          ELSE (avg_rw_rating.avg_rw_rating * avg_rw_rating.count - avg_rw_rating.weight) /
                                                (avg_rw_rating.count - 1) END adj_avg_rw_rating
                                            FROM (
                                                SELECT wrr.target_id, wrr.origin_id, wrr.weight, avg_rw_rating, count
                                                FROM crowdsourcing_workerrequesterrating wrr
                                                INNER JOIN (
                                                    SELECT recent_req_rating.target_id, AVG(recent_req_rating.weight) AS avg_rw_rating, 
                                                        COUNT(recent_req_rating.target_id)
                                                    FROM (
                                                        SELECT wrr.weight, wrr.target_id
                                                        FROM crowdsourcing_workerrequesterrating wrr
                                                        INNER JOIN (
                                                            SELECT origin_id, target_id, MAX(last_updated) AS max_date
                                                            FROM crowdsourcing_workerrequesterrating
                                                            GROUP BY origin_id, target_id
                                                        ) most_recent
                                                        ON most_recent.origin_id=wrr.origin_id AND most_recent.target_id=wrr.target_id
                                                        AND wrr.last_updated=most_recent.max_date AND wrr.target_id=%(worker_profile)s
                                                        AND wrr.origin_type='requester'
                                                    ) recent_req_rating
                                                    GROUP BY recent_req_rating.target_id
                                                ) avg_rw_rating
                                                ON wrr.target_id=avg_rw_rating.target_id
                                                INNER JOIN (
                                                    SELECT origin_id, target_id, MAX(last_updated) AS max_date
                                                    FROM crowdsourcing_workerrequesterrating 
                                                    GROUP BY origin_id, target_id
                                                ) most_recent
                                                ON wrr.origin_id = most_recent.origin_id AND wrr.target_id = most_recent.target_id AND
                                                wrr.last_updated=most_recent.max_date AND wrr.origin_type='requester'
                                            ) avg_rw_rating
                                        ) rw_rating
                                        ON owner_id=rw_rating.origin_id
                                        INNER JOIN (
                                            SELECT id,
                                            CASE WHEN elapsed_time > hard_deadline THEN 0
                                            WHEN elapsed_time/hard_deadline > submitted_tasks/total_tasks
                                            THEN min_rating * (1 - (elapsed_time/hard_deadline - submitted_tasks/total_tasks))
                                            ELSE min_rating END imputed_min_rating
                                            FROM (
                                                SELECT m.id, m.min_rating, COALESCE(submitted_tasks, 0) as submitted_tasks,
                                                (num_tasks * m.repetition) AS total_tasks,
                                                EXTRACT('EPOCH' FROM NOW() - m.created_timestamp) AS elapsed_time,
                                                module_length AS hard_deadline
                                                FROM crowdsourcing_module m
                                                INNER JOIN (
                                                    SELECT module_id, COUNT(id) AS num_tasks
                                                    FROM crowdsourcing_task
                                                    GROUP BY module_id
                                                ) tasks_per_module
                                                ON m.id=module_id
                                                LEFT OUTER JOIN (
                                                    SELECT module_id, COUNT(submitted_tasks) as submitted_tasks
                                                    FROM (
                                                        SELECT t.module_id, t.id, submitted_tasks
                                                        FROM crowdsourcing_task t
                                                        INNER JOIN ( 
                                                            SELECT task_id, COUNT(task_id) AS submitted_tasks
                                                            FROM (
                                                                SELECT task_worker_id, task_id
                                                                FROM crowdsourcing_taskworkerresult
                                                                INNER JOIN (
                                                                    SELECT task_id, id
                                                                    FROM crowdsourcing_taskworker
                                                                    GROUP BY task_id, id
                                                                ) tw
                                                                ON tw.id = task_worker_id
                                                                GROUP BY task_worker_id, task_id
                                                            ) tw_by_task
                                                        GROUP BY task_id
                                                        ) submit_by_task
                                                        ON t.id=task_id
                                                    ) submit_with_module
                                                    GROUP BY module_id
                                                ) task_count_by_module
                                                ON task_count_by_module.module_id = m.id
                                                INNER JOIN (
                                                    SELECT m.id, 
                                                    CASE WHEN num_active_workers=0 THEN (m.repetition * m.task_time * 60 * COUNT(t.id))
                                                    ELSE (m.repetition * m.task_time * 60 * COUNT(t.id) / num_active_workers) END module_length
                                                    FROM crowdsourcing_module m
                                                    INNER JOIN crowdsourcing_task t ON t.module_id=m.id
                                                    INNER JOIN (
                                                        SELECT COUNT(*) AS num_active_workers
                                                        FROM (
                                                            SELECT w.id, EXTRACT('EPOCH' FROM NOW() - up.last_active) AS elapsed
                                                            FROM crowdsourcing_worker w
                                                            INNER JOIN crowdsourcing_userprofile up ON profile_id=up.id
                                                        ) worker_last_active
                                                        WHERE elapsed IS NOT NULL AND elapsed < EXTRACT('EPOCH' FROM INTERVAL '1 day')
                                                    ) mod_task_workers
                                                    ON TRUE
                                                    GROUP BY m.id, num_active_workers
                                                ) module_time
                                                ON module_time.id=m.id
                                            ) cascade_data
                                        ) cascade_calc
                                        ON cascade_calc.id = m.id
                                    ) cascade_all
                                ) cascade_agg
                                WHERE imputed_rw_rating > imputed_min_rating
                            ) cascade_cond
                            INNER JOIN crowdsourcing_requester r ON cascade_cond.owner_id = r.id
                            INNER JOIN crowdsourcing_userprofile u ON r.profile_id = u.id
                            LEFT OUTER JOIN (
                                SELECT wrr.target_id, wrr.weight
                                FROM crowdsourcing_workerrequesterrating wrr
                                INNER JOIN(
                                    SELECT target_id, MAX(last_updated) AS max_date
                                    FROM crowdsourcing_workerrequesterrating
                                    WHERE origin_type='worker' AND origin_id=%(worker_profile)s
                                    GROUP BY target_id
                                ) most_recent
                                ON wrr.target_id = most_recent.target_id AND wrr.last_updated = most_recent.max_date AND wrr.origin_type='worker'
                                AND wrr.origin_id=%(worker_profile)s
                            ) wr_rating
                            ON u.id = wr_rating.target_id
                            LEFT OUTER JOIN (
                                SELECT target_id, AVG(weight) AS avg_wr_rating
                                FROM (
                                    SELECT wrr.target_id, wrr.weight
                                    FROM crowdsourcing_workerrequesterrating wrr
                                    INNER JOIN (
                                        SELECT origin_id, target_id, MAX(last_updated) AS max_date
                                        FROM crowdsourcing_workerrequesterrating 
                                        GROUP BY origin_id, target_id
                                    ) most_recent
                                    ON most_recent.origin_id=wrr.origin_id AND most_recent.target_id=wrr.target_id AND wrr.last_updated=most_recent.max_date
                                    AND wrr.origin_id <> %(worker_profile)s AND wrr.origin_type='worker'
                                ) recent_wr_rating
                                GROUP BY target_id
                            ) avg_wr_rating
                            ON avg_wr_rating.target_id = u.id
                        ) boomerang
                        WHERE owner_id<>%(owner)s
                    ) boomeranged_modules
                    INNER JOIN crowdsourcing_project p
                    ON p.id=boomeranged_modules.project_id
                    GROUP BY p.id, p.name, p.description, imputed_wr_rating
                    ORDER BY imputed_wr_rating desc, p.id desc;
                '''
            projects = Project.objects.select_related('modules').\
                raw(query, params={'worker_profile': request.user.userprofile.id,
                                   'owner': requester_id})
            #for project in projects:
                #m = Module.objects.get(id=project.module_id)
                #m.min_rating = project.imputed_rating
                #m.save()
            #    pass

            '''
                TODO query above has to be rewritten and min_rating has to be updated, disabling it now because we
                dont need cascading for CHI, it has to be optimized too -DM
            '''
            projects_serialized = ProjectSerializer(projects, fields=('id', 'name', 'description', 'modules', 'owner'),
                                                    many=True, context={'request': request})
            return Response(projects_serialized.data)
        except:
            return Response([])

    @list_route(methods=['GET'])
    def requester_projects(self, request, **kwargs):
        projects = request.user.userprofile.requester.project_owner.all()
        serializer = ProjectSerializer(instance=projects, many=True, fields=('id', 'name', 'module_count'),
                                       context={'request': request})
        return Response(serializer.data)



    @list_route(methods=['get'])
    def get_bookmarked_projects(self, request, **kwargs):
        user_profile = request.user.userprofile
        bookmarked_projects = models.BookmarkedProjects.objects.all().filter(profile=user_profile)
        projects = bookmarked_projects.values('project', ).all()
        project_instances = models.Project.objects.all().filter(pk__in=projects)
        serializer = ProjectSerializer(instance=project_instances, many=True, context={'request': request})
        return Response(serializer.data, 200)

    def create(self, request, *args, **kwargs):
        project_serializer = ProjectSerializer(data=request.data)
        if project_serializer.is_valid():
            project_serializer.create(owner=request.user.userprofile)
            return Response({'status': 'Project created'})
        else:
            return Response(project_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        project_serializer = ProjectSerializer()
        project = self.get_object()
        project_serializer.delete(project)
        return Response({'status': 'deleted project'})


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsProjectOwnerOrCollaborator, IsAuthenticated]

    @list_route(methods=['get'])
    def get_last_milestone(self, request, **kwargs):
        last_milestone = Module.objects.all().filter(project=request.query_params.get('projectId')).last()
        module_serializer = ModuleSerializer(instance=last_milestone, context={'request': request})
        return Response(module_serializer.data)

    def create(self, request, *args, **kwargs):
        module_serializer = ModuleSerializer(data=request.data)
        if module_serializer.is_valid():
            module_serializer.create(owner=request.user.userprofile)
            return Response({'status': 'Module created'})
        else:
            return Response(module_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        module_serializer = ModuleSerializer(instance=instance, data=request.data, partial=True)
        if module_serializer.is_valid():
            module_serializer.update(instance=instance, validated_data=module_serializer.validated_data)
            return Response(data={"message": "Module updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(data=module_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'])
    def list_by_project(self, request, **kwargs):
        milestones = Module.objects.filter(project=request.query_params.get('project_id'))
        module_serializer = ModuleSerializer(instance=milestones, many=True,
                                             fields=('id', 'name', 'age', 'total_tasks', 'status'), context={'request': request})
        response_data = {
            'project_name': milestones[0].project.name,
            'project_id': request.query_params.get('project_id'),
            'modules': module_serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def list_comments(self, request, **kwargs):
        comments = models.ModuleComment.objects.filter(module=kwargs['pk'])
        serializer = ModuleCommentSerializer(instance=comments, many=True, fields=('comment', 'id',))
        response_data = {
            'module': kwargs['pk'],
            'comments': serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def post_comment(self, request, **kwargs):
        serializer = ModuleCommentSerializer(data=request.data)
        module_comment_data = {}
        if serializer.is_valid():
            comment = serializer.create(module=kwargs['pk'], sender=request.user.userprofile)
            module_comment_data = ModuleCommentSerializer(comment, fields=('id', 'comment',)).data

        return Response(module_comment_data, status.HTTP_200_OK)


class ModuleReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsReviewerOrRaterOrReadOnly]

    def get_queryset(self):
        queryset = ModuleReview.objects.all()
        moduleid = self.request.query_params.get('moduleid', None)
        queryset = ModuleReview.objects.filter(module__id=moduleid)
        return queryset

    serializer_class = ModuleReviewSerializer


class ModuleRatingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsReviewerOrRaterOrReadOnly]

    def get_queryset(self):
        moduleid = self.request.query_params.get('moduleid')
        if self.request.user.is_authenticated():
            queryset = ModuleRating.objects.filter(module_id=moduleid).filter(worker__profile__user=self.request.user)
        else:
            queryset = ModuleRating.objects.none()
        return queryset

    serializer_class = ModuleRatingSerializer


class ProjectRequesterViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ProjectRequesterSerializer
    queryset = ProjectRequester.objects.all()

    # TODO to be moved under Project
    def retrieve(self, request, *args, **kwargs):
        project_requester = get_object_or_404(self.queryset,
                                              project=get_object_or_404(Project.objects.all(), id=kwargs['pk']))
        serializer = ProjectRequesterSerializer(instance=project_requester)
        return Response(serializer.data, status.HTTP_200_OK)


class BookmarkedProjectsViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                                mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = BookmarkedProjects.objects.all()
    serializer_class = BookmarkedProjectsSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = BookmarkedProjectsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(profile=request.user.userprofile)
            return Response({"Status": "OK"})
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
