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
from crowdsourcing.models import Project


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
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

    @list_route()
    def get_project(self, request):
        try:
            projects = Project.objects.get(deleted=False)
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
        if project.deleted == True:
            return Response("Project does not exist!",
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            project_serialized = ProjectSerializer(project)
            return Response(project_serialized.data)


class ModuleViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Module
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer()
