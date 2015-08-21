from rest_framework import status, viewsets
from rest_framework.response import Response
from crowdsourcing.serializers.project import *
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.models import Module, Category, Project, Requester, ProjectRequester, \
    ModuleReview, ModuleRating, BookmarkedProjects
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.permissions.util import IsOwnerOrReadOnly
from crowdsourcing.permissions.project import IsReviewerOrRaterOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch


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
            projects = Project.objects.raw('''
                select id, name, description, created_timestamp, last_updated, owner_id, case when weight is null
                and average_rating is not null then average_rating
                when weight is null and average_rating is null then 1.99
                when weight is not null and average_rating is null then weight
                  else weight + 0.1 * average_rating END relevant_rating
                from (
                SELECT p.*, w.weight, avg.average_rating FROM crowdsourcing_project p
                  INNER JOIN crowdsourcing_requester r ON p.owner_id = r.id
                  INNER JOIN crowdsourcing_userprofile u ON r.profile_id = u.id
                  LEFT OUTER JOIN crowdsourcing_workerrequesterrating w
                        ON u.id = w.target_id AND w.type='worker' AND w.origin_id=%s
                  LEFT OUTER JOIN (SELECT target_id, AVG(CASE WHEN res.count=1 AND res.origin_id=%s
                    THEN NULL ELSE res.weight END) AS average_rating from
                    (SELECT wr.*, count FROM crowdsourcing_workerrequesterrating wr
                    INNER JOIN (SELECT target_id, COUNT(*) as count from crowdsourcing_workerrequesterrating
                        WHERE type='worker' GROUP BY target_id) temp ON wr.target_id=temp.target_id) res 
                        GROUP BY target_id) avg
                        ON avg.target_id = u.id) calc WHERE owner_id<>%s 
                ORDER BY relevant_rating desc
            ''', params=[request.user.userprofile.id, request.user.userprofile.id, request.user.userprofile.requester.id])
            projects_serialized = ProjectSerializer(projects, many=True)
            return Response(projects_serialized.data)
        except:
            return Response([])

    @list_route(methods=['GET'])
    def requester_projects(self, request, **kwargs):
        projects = request.user.userprofile.requester.project_owner.all()
        serializer = ProjectSerializer(instance=projects, many=True, fields=('id', 'name', 'module_count'))
        return Response(serializer.data)

    @list_route(methods=['get'])
    def get_bookmarked_projects(self, request, **kwargs):
        user_profile = request.user.userprofile
        bookmarked_projects = models.BookmarkedProjects.objects.all().filter(profile=user_profile)
        projects = bookmarked_projects.values('project', ).all()
        project_instances = models.Project.objects.all().filter(pk__in=projects)
        serializer = ProjectSerializer(instance=project_instances, many=True)
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
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]

    @list_route(methods=['get'])
    def get_last_milestone(self, request, **kwargs):
        last_milestone = Module.objects.all().filter(project=request.query_params.get('projectId')).last()
        module_serializer = ModuleSerializer(instance=last_milestone)
        return Response(module_serializer.data)

    def create(self, request, *args, **kwargs):
        module_serializer = ModuleSerializer(data=request.data)
        if module_serializer.is_valid():
            module_serializer.create(owner=request.user.userprofile)
            return Response({'status': 'Module created'})
        else:
            return Response(module_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'])
    def list_by_project(self, request, **kwargs):
        milestones = Module.objects.filter(project=request.query_params.get('project_id'))
        module_serializer = ModuleSerializer(instance=milestones, many=True,
                                             fields=('id', 'name', 'age', 'total_tasks', 'status'))
        response_data = {
            'project_name': milestones[0].project.name,
            'project_id': request.query_params.get('project_id'),
            'modules': module_serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)


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
