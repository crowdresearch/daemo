from django.db.models import Q

__author__ = 'elsabakiu, neilthemathguy, dmorina, shirishgoyal'


from rest_framework import status, viewsets
from rest_framework.response import Response
from crowdsourcing.serializers.project import *
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.models import Module, Category, Project, Requester, ProjectRequester
from crowdsourcing.permissions.project import IsProjectCollaborator
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

    @detail_route(methods=['post'], permission_classes=[IsProjectCollaborator])
    def update_project(self, request, pk=None):
        project_serializer = ProjectSerializer(data=request.data)
        project = self.get_object()
        if project_serializer.is_valid():
            project_serializer.update(project,project_serializer.validated_data)

            return Response({'status': 'updated project'})
        else:
            return Response(project_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = Project.objects.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        project_serializer = ProjectSerializer()
        project = self.get_object()
        project_serializer.delete(project)
        return Response({'status': 'deleted project'})

    @list_route(methods=['get'])
    def search(self, request):
        search_text = request.GET.get('search', '')

        queryset = Project.objects.filter(Q(name__contains=search_text))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Module
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer 


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