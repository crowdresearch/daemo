from crowdsourcing.forms import *
from csp import settings
from rest_framework import status, views as rest_framework_views, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
import hashlib, random
from crowdsourcing.serializers.project import *
from crowdsourcing.models import *
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.serializers.user import UserProfileSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    """
        This class handles user view sets
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_value_regex = '[^/]+'
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create()
            return Response(serializer.data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated,])
    def change_password(self, request, username=None):
        user = request.user
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            #serializer.change_password()
            return Response({"message": "Password updated successfully."}, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def authenticate(self, request):
        serializer = UserSerializer()
        response_data, status = serializer.authenticate(request)
        return Response(response_data, status)
