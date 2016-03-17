from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import mixins
from django.shortcuts import get_object_or_404

from crowdsourcing.models import *
from crowdsourcing.serializers.user import UserProfileSerializer, UserSerializer, UserPreferencesSerializer
from crowdsourcing.permissions.user import CanCreateAccount
from crowdsourcing.utils import get_model_or_none


class UserViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        This class handles user view sets
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_value_regex = '[^/]+'
    lookup_field = 'username'
    permission_classes = [CanCreateAccount]

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(validate_non_fields=True, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.create()
            return Response(serializer.data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'], permission_classes=[IsAdminUser, ])
    def hard_create(self, request):
        return self.create(request)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated, ])
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

    @list_route(methods=['post'])
    def activate_account(self, request):
        """
            this handles the account activation after the user follows the link from his/her email.
        """
        from django.contrib.auth.models import User

        try:
            activation_key = request.data.get('activation_key', None)
            activate_user = RegistrationModel.objects.get(activation_key=activation_key)
            if activate_user:
                user = User.objects.get(id=activate_user.user_id)
                user.is_active = 1
                user.save()
                activate_user.delete()
                return Response(data={"message": "Account activated successfully"}, status=status.HTTP_200_OK)
        except RegistrationModel.DoesNotExist:
            return Response(data={"message": "Your account couldn't be activated. It may already be active."},
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def forgot_password(self, request):
        email = request.data.get('email', '')
        user = get_object_or_404(User, email=email)
        serializer = UserSerializer(context={'request': request})
        serializer.send_forgot_password(user=user)
        return Response(data={
            'message': 'Email sent.'
        }, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def reset_password(self, request):
        password = request.data.get('password', 'N')
        password_reset_model = get_model_or_none(PasswordResetModel, reset_key=request.data.get('reset_key', ''))
        serializer = UserSerializer(context={'request': request})
        data, http_status = serializer.reset_password(reset_model=password_reset_model, password=password)
        return Response(data=data, status=http_status)

    @list_route(methods=['post'])
    def ignore_password_reset(self, request):
        password_reset_model = get_object_or_404(PasswordResetModel, reset_key=request.data.get('reset_key', ''))
        serializer = UserSerializer(context={'request': request})
        data, http_status = serializer.ignore_reset_password(reset_model=password_reset_model)
        return Response(data=data, status=http_status)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
        This class handles user profile rendering, changes and so on.
    """
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    lookup_value_regex = '[^/]+'
    lookup_field = 'user__username'

    def create(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create()
            return Response(serializer.validated_data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def update_profile(self, request, user__username=None):
        serializer = UserProfileSerializer(instance=self.get_object(), data=request.data)
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

    def retrieve(self, request, user__username=None):
        profile = get_object_or_404(self.queryset, user__username=user__username)
        serializer = self.serializer_class(instance=profile)
        return Response(serializer.data)


class UserPreferencesViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserPreferencesSerializer
    queryset = UserPreferences.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_value_regex = '[^/]+'
    lookup_field = 'user__username'

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(self.queryset, user=request.user)
        serializer = UserPreferencesSerializer(instance=user)
        return Response(serializer.data)

    def update(self, request, user__username=None):
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        serializer = self.serializer_class(instance=preferences, data=request.data)
        if serializer.is_valid():
            serializer.update()
            return Response({'status': 'updated preferences'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user_preference = UserPreferences.objects.get(user=request.user)
        serializer = UserPreferencesSerializer(user_preference)
        return Response(serializer.data)
