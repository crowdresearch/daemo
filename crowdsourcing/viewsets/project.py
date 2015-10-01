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
                    SELECT p.id, p.name, p.description, Max(mod.relevant_requester_rating) FROM (

                    SELECT id, name, description, created_timestamp, last_updated, owner_id, project_id, imputed_rating,
                        CASE WHEN real_weight IS NULL AND average_requester_rating IS NOT NULL THEN average_requester_rating
                        WHEN real_weight IS NULL AND average_requester_rating IS NULL THEN 1.99
                        WHEN real_weight IS NOT NULL AND average_requester_rating IS NULL THEN real_weight
                        ELSE real_weight + 0.1 * average_requester_rating END relevant_requester_rating
                        FROM (
                            SELECT rnk.*, wrr.weight as real_weight, avg.average_requester_rating FROM (

                    --This fetches the modules according to cascading release
                    SELECT evr.*
                    FROM(
                        SELECT avgrat.*, CASE WHEN weight IS NULL
                            AND adj_average_worker_rating IS NOT NULL THEN adj_average_worker_rating
                            WHEN weight IS NULL AND adj_average_worker_rating IS NULL THEN 1.99
                            WHEN weight IS NOT NULL AND adj_average_worker_rating IS NULL THEN weight
                            ELSE weight + 0.1 * adj_average_worker_rating END worker_relevant_rating
                        FROM (
                            SELECT m.*, als.weight, als.adj_average_worker_rating, imputed_rating FROM crowdsourcing_module m
                                INNER JOIN crowdsourcing_requester r ON m.owner_id = r.id
                                INNER JOIN crowdsourcing_userprofile u ON r.profile_id = u.id
                                LEFT OUTER JOIN
                                    (SELECT w.* FROM crowdsourcing_workerrequesterrating w
                                    INNER JOIN(
                                        SELECT origin_id, MAX(last_updated) AS max_date FROM crowdsourcing_workerrequesterrating
                                            WHERE origin_type='requester' AND target_id = %(worker_profile)s GROUP BY origin_id) tb
                                        ON w.origin_id = tb.origin_id AND w.last_updated = tb.max_date
                                        AND w.origin_type='requester' AND w.target_id=%(worker_profile)s) w
                                    ON u.id = w.origin_id
                                LEFT OUTER JOIN (
                                    SELECT temp.origin_id, temp.target_id, temp.average_worker_rating, temp.count, temp.weight,
                                         (temp.average_worker_rating * temp.count - temp.weight) /
                                         (temp.count-1) as adj_average_worker_rating FROM
                                    (SELECT w.*, average_worker_rating, count from crowdsourcing_workerrequesterrating w
                                    INNER JOIN
                                    (SELECT target_id, AVG(weight) AS average_worker_rating, COUNT(target_id) from
                                    (SELECT wr.* FROM crowdsourcing_workerrequesterrating wr
                                    INNER JOIN (
                                        SELECT origin_id, target_id, MAX(last_updated) AS max_date
                                            FROM crowdsourcing_workerrequesterrating
                                        GROUP BY origin_id, target_id) fltr
                                        ON fltr.origin_id=wr.origin_id AND fltr.target_id=wr.target_id AND
                                            wr.last_updated=fltr.max_date AND wr.target_id=%(worker_profile)s AND wr.origin_type='requester') sult
                                        GROUP BY target_id) avgreq
                                    ON w.target_id=avgreq.target_id
                                    INNER JOIN (
                                    SELECT origin_id, target_id, MAX(last_updated) AS max_date
                                            FROM crowdsourcing_workerrequesterrating
                                        GROUP BY origin_id, target_id
                                    ) tmp ON w.origin_id = tmp.origin_id AND w.target_id = tmp.target_id AND
                                            w.last_updated=tmp.max_date AND w.origin_type='requester') temp) als
                                    ON owner_id=als.origin_id
                            INNER JOIN (
                                SELECT id, CASE WHEN elapsed_time > hard_deadline THEN 0
                                WHEN elapsed_time/hard_deadline > submitted_tasks/total_tasks THEN
                                    min_rating * (1 - (elapsed_time/hard_deadline - submitted_tasks/total_tasks))
                                ELSE min_rating END imputed_rating
                                FROM (
                                    SELECT m.*, COALESCE(submitted_tasks, 0) as submitted_tasks,
                                        (num_tasks * m.repetition) AS total_tasks,
                                        EXTRACT('EPOCH' FROM NOW() - m.created_timestamp) AS elapsed_time,
                                        EXTRACT('EPOCH' FROM INTERVAL '1 day') AS hard_deadline
                                    FROM crowdsourcing_module m
                                    INNER JOIN (SELECT module_id, COUNT(id) AS
                                        num_tasks FROM crowdsourcing_task GROUP BY module_id) tsk
                                        ON m.id=module_id
                                    LEFT OUTER JOIN (SELECT task_id, COUNT(task_id) AS submitted_tasks FROM
                                        (SELECT task_worker_id, task_id FROM crowdsourcing_taskworkerresult
                                        INNER JOIN (SELECT task_id, id FROM crowdsourcing_taskworker GROUP BY task_id, id) tw
                                            ON tw.id = task_worker_id GROUP BY task_worker_id, task_id) tmp GROUP BY task_id) sbmt
                                    ON sbmt.task_id = id) calc) imprat ON imprat.id = m.id) avgrat)
                                        evr WHERE worker_relevant_rating > imputed_rating) rnk

                    INNER JOIN crowdsourcing_requester rq ON rnk.owner_id = rq.id
                    INNER JOIN crowdsourcing_userprofile up ON rq.profile_id = up.id
                    LEFT OUTER JOIN
                        (SELECT w.* FROM crowdsourcing_workerrequesterrating w
                        INNER JOIN(
                            SELECT target_id, MAX(last_updated) AS max_date FROM crowdsourcing_workerrequesterrating
                                WHERE origin_type='worker' AND origin_id=%(worker_profile)s GROUP BY target_id) tb
                        ON w.target_id = tb.target_id AND w.last_updated = tb.max_date AND w.origin_type='worker'
                        AND w.origin_id=%(worker_profile)s) wrr
                        ON up.id = wrr.target_id
                    LEFT OUTER JOIN (
                        SELECT target_id, AVG(weight) AS average_requester_rating from
                        (SELECT wr.* FROM crowdsourcing_workerrequesterrating wr
                        INNER JOIN (
                            SELECT origin_id, target_id, MAX(last_updated) AS max_date FROM crowdsourcing_workerrequesterrating
                            GROUP BY origin_id, target_id) fltr
                        ON fltr.origin_id=wr.origin_id AND fltr.target_id=wr.target_id AND wr.last_updated=fltr.max_date
                        AND wr.origin_id <> %(worker_profile)s AND wr.origin_type='worker') sult GROUP BY target_id) avg
                    ON avg.target_id = up.id) calc WHERE owner_id<>%(owner)s
                    ) mod INNER JOIN crowdsourcing_project p ON p.id=mod.project_id
                    GROUP BY p.id, p.name, p.description, relevant_requester_rating
                    ORDER BY relevant_requester_rating desc, p.id desc;
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
