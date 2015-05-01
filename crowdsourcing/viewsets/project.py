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


class ProjectViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Project
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer()

    lookup_value_regex = '[^/]+'

    @detail_route(methods=['post'])
    def update_project(self, request, id=None):
        serializer = ProjectSerializer(data=request.data)
        project = self.get_object()
        if serializer.is_valid():
            serializer.update(project,serializer.validated_data)

            return Response({'status': 'updated project'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route()
    def get_profile(self, request):
        projects = ProjectSerializer.objects.all()
        serializer = ProjectSerializer(projects)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Module
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer()
