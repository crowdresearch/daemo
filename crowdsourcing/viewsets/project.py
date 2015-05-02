__author__ = 'elsabakiu'
#from provider.oauth2.models import RefreshToken, AccessToken
from crowdsourcing import models
from crowdsourcing.forms import *
from crowdsourcing.utils import *
from csp import settings
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView
from oauth2_provider.models import AccessToken, RefreshToken
from rest_framework import status, views as rest_framework_views, viewsets
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from crowdsourcing.serializers.project import *
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.models import Category, Project

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

    def list(self, request):
        try:
            category = Category.objects.all()
            categoriess_serialized = CategorySerializer(category)
            return Response(categoriess_serialized.data)
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

    @detail_route(methods=['post'])
    def update_project(self, request, id=None):
        project_serializer = ProjectSerializer(data=request.data)
        project = self.get_object()
        if project_serializer.is_valid():
            project_serializer.update(project,project_serializer.validated_data)

            return Response({'status': 'updated project'})
        else:
            return Response(project_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        try:
            projects = Project.objects.all()
            projects_serialized = ProjectSerializer(projects)
            return Response(projects_serialized.data)
        except:
            return Response([])

    def destroy(self, request, *args, **kwargs):
        project_serializer = ProjectSerializer()
        project = self.get_object()
        project_serializer.delete(project)
        return Response({'status': 'deleted project'})

    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        project_serialized = ProjectSerializer(project)
        return Response(project_serialized.data)


class ModuleViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Module
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer()
