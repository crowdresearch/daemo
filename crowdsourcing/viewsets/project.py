__author__ = 'elsabakiu, neilthemathguy, dmorina'


from rest_framework import status, viewsets
from rest_framework.response import Response
from crowdsourcing.serializers.project import *
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.models import Module, Category, Project, Requester, ProjectRequester, \
    ModuleReview, ModuleRating
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator
from crowdsourcing.permissions.util import IsOwnerOrReadOnly
from crowdsourcing.permissions.project import IsReviewerOrRaterOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from django.shortcuts import get_object_or_404


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(deleted=False)
    serializer_class = CategorySerializer

    @detail_route(methods=['post'])
    def update_category(self, request, id=None):
        category_serializer = CategorySerializer(data=request.data)
        category = self.get_object()
        if category_serializer.is_valid():
            category_serializer.update(category,category_serializer.validated_data)

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
    #permission_classes = [IsAuthenticated]

    @detail_route(methods=['post'], permission_classes=[IsProjectOwnerOrCollaborator])
    def update_project(self, request, pk=None):
        project_serializer = ProjectSerializer(data=request.data, partial=True)
        project = self.get_object()
        if project_serializer.is_valid():
            project_serializer.update(project,project_serializer.validated_data)

            return Response({'status': 'updated project'})
        else:
            return Response(project_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            projects = Project.objects.all()
            projects_serialized = ProjectSerializer(projects, many=True)
            return Response(projects_serialized.data)
        except:
            return Response([])

    @list_route(methods=['GET'])
    def requesterprojects(self, request, **kwargs):
        projects = request.user.user_profile.requester.project_owner.all()
        serializer = ProjectSerializer(instance = projects,many = True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        project_serializer = ProjectSerializer(data=request.data)
        if project_serializer.is_valid():
            project_serializer.create(owner=request.user.userprofile.requester)
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
    permission_classes=[IsOwnerOrReadOnly]


# To get reviews of a module pass module id as an parameter of get request like /api/modulereview/?moduleid=1
class ModuleReviewViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import ModuleReview
    permission_classes=[IsReviewerOrRaterOrReadOnly]

    def get_queryset(self):
        queryset = ModuleReview.objects.all()
        moduleid=self.request.query_params.get('moduleid',None)
        queryset = ModuleReview.objects.filter(module__id=moduleid)
        return queryset

    serializer_class = ModuleReviewSerializer

# To get rating of a module given by logged in user, pass module id as an parameter of get request like /api/modulerating/?moduleid=1

class ModuleRatingViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import ModuleRating
    permission_classes=[IsReviewerOrRaterOrReadOnly]
    def get_queryset(self):
        moduleid = self.request.query_params.get('moduleid')
        if self.request.user.is_authenticated():
            queryset = ModuleRating.objects.filter(module_id = moduleid).filter(worker__profile__user = self.request.user)
        else:
            queryset = ModuleRating.objects.none()
        return queryset
    serializer_class = ModuleRatingSerializer



class ProjectRequesterViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ProjectRequesterSerializer
    queryset = ProjectRequester.objects.all()
    #permission_classes=(IsProjectCollaborator,)
    #TODO to be moved under Project
    def retrieve(self, request, *args, **kwargs):
        project_requester = get_object_or_404(self.queryset, project=get_object_or_404(Project.objects.all(),id=kwargs['pk']))
        serializer = ProjectRequesterSerializer(instance=project_requester)
        return Response(serializer.data, status.HTTP_200_OK)
