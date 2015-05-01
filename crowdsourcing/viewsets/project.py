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
from rest_framework import generics
from rest_framework import status, views as rest_framework_views, viewsets
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from crowdsourcing.serializers.project import *


class ProjectViewSet(generics.ListCreateAPIView):
    from crowdsourcing.models import Project
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer()


class ModuleViewSet(generics.ListCreateAPIView):
    from crowdsourcing.models import Module
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer()
