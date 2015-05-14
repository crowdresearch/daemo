from csp import settings
from rest_framework import status, views as rest_framework_views, viewsets
from rest_framework.response import Response
import hashlib, random
from crowdsourcing.serializers.project import *
from crowdsourcing.models import *
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.serializers.user import UserProfileSerializer, UserSerializer, UserPreferencesSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from django.shortcuts import get_object_or_404


class UserViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        This class handles user view sets
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_value_regex = '[^/]+'
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(validate_non_fields=True, data=request.data)
        if serializer.is_valid():
            serializer.create()
            return Response(serializer.data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated,])
    def change_password(self, request, username=None):
        user = request.user
        serializer = UserSerializer(validate_non_fields=True, instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.change_password()
            return Response({"message": "Password updated successfully."}, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def change_username(self, request, username=None):
        user = request.user
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.change_username()
            return Response({"message": "Username updated successfully."})
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def authenticate(self, request):
        serializer = UserSerializer()
        response_data, status = serializer.authenticate(request)
        return Response(response_data, status)

    def retrieve(self, request, username=None):
        user = get_object_or_404(self.queryset, username=username)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)

class UserProfileViewSet(viewsets.ModelViewSet):
    """
        This class handles user profile rendering, changes and so on.
    """
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    lookup_value_regex = '[^/]+'
    lookup_field = 'user__username'
    @detail_route(methods=['post'])
    def update_profile(self, request, user__username=None):
        serializer = UserProfileSerializer(instance=self.get_object(),data=request.data)
        if serializer.is_valid():
            serializer.update()
            return Response({'status': 'updated profile'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route()
    def get_profile(self, request):
        user_profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(user_profiles)
        return Response(serializer.data)


class UserPreferencesViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserPreferencesSerializer
    queryset = UserPreferences.objects.all()
    permission_classes = [IsAuthenticated]
    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(self.queryset, user=request.user)
        serializer = UserPreferencesSerializer(instance=user)
        return Response(serializer.data)