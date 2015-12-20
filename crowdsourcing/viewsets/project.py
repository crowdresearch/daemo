from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from crowdsourcing.models import Module, Category, Project, ProjectRequester, \
    ModuleReview, ModuleRating, BookmarkedProjects
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.permissions.project import IsReviewerOrRaterOrReadOnly
from crowdsourcing.serializers.project import *
from crowdsourcing.serializers.file import *
from django.db import transaction


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
        try:
            projects = self.queryset
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
        create_module = request.data.get('create_milestone', False)
        project_serializer = ProjectSerializer(data=request.data)
        if project_serializer.is_valid():
            response_data = {}
            with transaction.atomic():
                data = project_serializer.create(owner=request.user.userprofile, create_module=create_module)
                response_data = {
                    "id": data.id,
                    "create_milestone": create_module
                }
            return Response(data=response_data, status=status.HTTP_200_OK)
        else:
            return Response(project_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        project_serializer = ProjectSerializer()
        project = self.get_object()
        project_serializer.delete(project)
        return Response({'status': 'deleted project'})


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.filter(deleted=False)
    serializer_class = ModuleSerializer
    permission_classes = [IsProjectOwnerOrCollaborator, IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        module_object = self.get_object()
        serializer = ModuleSerializer(instance=module_object,
                                      fields=('id', 'name', 'price', 'repetition',
                                              'is_prototype', 'templates', 'project', 'status', 'batch_files'))

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def fork(self, request, **kwargs):
        instance = self.get_object()
        module_serializer = ModuleSerializer(instance=instance, data=request.data, partial=True,
                                             fields=('id', 'name', 'price', 'repetition',
                                                     'is_prototype', 'templates', 'project', 'status', 'batch_files'))
        if module_serializer.is_valid():
            with transaction.atomic():
                module_serializer.fork()
            return Response(data=module_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=module_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'])
    def get_last_milestone(self, request, **kwargs):
        last_milestone = Module.objects.all().filter(project=request.query_params.get('projectId')).last()
        module_serializer = ModuleSerializer(instance=last_milestone, context={'request': request})
        return Response(module_serializer.data)

    @list_route(methods=['GET'])
    def requester_modules(self, request, **kwargs):
        modules = request.user.userprofile.requester.module_owner.all().filter(deleted=False)
        serializer = ModuleSerializer(instance=modules, many=True,
                                      fields=('id', 'name', 'age', 'total_tasks', 'status'),
                                      context={'request': request})
        return Response(serializer.data)

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
            with transaction.atomic():
                module_serializer.update()
            return Response(data={"message": "Module updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(data=module_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project = instance.project
        if project.modules.count() == 1:
            project.delete()
        else:
            module_serializer = ModuleSerializer(instance=instance)
            module_serializer.delete(instance)
        return Response(data={"message": "Module deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['get'])
    def list_by_project(self, request, **kwargs):
        milestones = Module.objects.filter(project=request.query_params.get('project_id'))
        module_serializer = ModuleSerializer(instance=milestones, many=True,
                                             fields=('id', 'name', 'age', 'total_tasks', 'status'),
                                             context={'request': request})
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

    @list_route(methods=['get'])
    def list_feed(self, request, **kwargs):
        query = '''
            WITH modules AS (
                SELECT
                  ratings.module_id,
                  ratings.min_rating new_min_rating,
                  requester_ratings.requester_rating
                FROM get_min_ratings() ratings
                  LEFT OUTER JOIN (SELECT requester_id, CASE WHEN requester_rating IS NULL AND requester_avg_rating
                                        IS NOT NULL THEN requester_avg_rating
                                    WHEN requester_rating IS NULL AND requester_avg_rating IS NULL THEN 1.99
                                    WHEN requester_rating IS NOT NULL AND requester_avg_rating IS NULL
                                    THEN requester_rating
                                    ELSE requester_rating + 0.1 * requester_avg_rating END requester_rating
                                   FROM get_requester_ratings(%(worker_profile)s)) requester_ratings
                    ON requester_ratings.requester_id = ratings.owner_id
                  LEFT OUTER JOIN (SELECT requester_id, CASE WHEN worker_rating IS NULL AND worker_avg_rating
                                        IS NOT NULL THEN worker_avg_rating
                                    WHEN worker_rating IS NULL AND worker_avg_rating IS NULL THEN 1.99
                                    WHEN worker_rating IS NOT NULL AND worker_avg_rating IS NULL THEN worker_rating
                                    ELSE worker_rating + 0.1 * worker_avg_rating END worker_rating
                                   FROM get_worker_ratings(%(worker_profile)s)) worker_ratings
                    ON worker_ratings.requester_id = ratings.owner_id
                    and worker_ratings.worker_rating>=ratings.min_rating
                ORDER BY requester_rating desc)
            UPDATE crowdsourcing_module m set min_rating=modules.new_min_rating
            FROM modules
            where modules.module_id=m.id
            RETURNING m.id, m.name, m.price, m.owner_id, m.created_timestamp, m.allow_feedback;
        '''
        modules = Module.objects.raw(query, params={'worker_profile': request.user.userprofile.id})
        module_serializer = ModuleSerializer(instance=modules, many=True,
                                             fields=('id', 'name', 'age', 'total_tasks',
                                                     'status', 'available_tasks', 'has_comments',
                                                     'allow_feedback', 'price', 'task_time', 'owner'),
                                             context={'request': request})

        return Response(data=module_serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def attach_file(self, request, **kwargs):
        serializer = ModuleBatchFileSerializer(data=request.data, fields=('batch_file',))
        if serializer.is_valid():
            module_file = serializer.create(module=kwargs['pk'])
            file_serializer = ModuleBatchFileSerializer(instance=module_file)
            return Response(data=file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['delete'])
    def delete_file(self, request, **kwargs):
        batch_file = request.data.get('batch_file', None)
        instances = models.ModuleBatchFile.objects.filter(batch_file=batch_file)
        if instances.count() == 1:
            models.BatchFile.objects.filter(id=batch_file).delete()
        else:
            models.ModuleBatchFile.objects.filter(batch_file_id=batch_file, module_id=kwargs['pk']).delete()
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)


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
