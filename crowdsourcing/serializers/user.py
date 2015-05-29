__author__ = ['dmorina', 'shirish']

import uuid
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import ugettext_lazy as _

from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json, hashlib, random, re
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from crowdsourcing.validators.utils import *
from csp import settings
from crowdsourcing.emails import send_activation_email
from crowdsourcing.utils import get_model_or_none, Oauth2Utils, get_next_unique_id
from rest_framework import status


class UserProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username', read_only=True)
    verified = serializers.ReadOnlyField()

    class Meta:
        model = models.UserProfile
        fields = ( 'user_username', 'gender', 'birthday', 'verified', 'address', 'nationality',
                   'picture', 'friends', 'roles', 'created_timestamp', 'languages')

    def create(self, **kwargs):
        address_data = self.validated_data.pop('address')
        address = models.Address.objects.create(**address_data)

        return models.UserProfile.objects.create(address=address, **self.validated_data)

    def update(self, **kwargs):
        address = self.instance.address
        address_data = self.validated_data.pop('address')

        address.city = address_data.get('city', address.city)
        address.country = address_data.get('country', address.country)
        address.street = address_data.get('street', address.street)

        address.save()

        self.instance.gender = self.validated_data.get('gender', self.instance.gender)
        self.instance.birthday = self.validated_data.get('birthday', self.instance.birthday)
        self.instance.verified = self.validated_data.get('verified', self.instance.verified)
        self.instance.picture = self.validated_data.get('picture', self.instance.picture)
        self.instance.save(address=address)
        return self.instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = {'id', 'name'}


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserRole


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Friendship


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserPreferences
        fields = ('language', 'currency', 'login_alerts')


class UserSerializer(serializers.ModelSerializer):
    last_login = serializers.DateTimeField(required=False, read_only=True)
    date_joined = serializers.DateTimeField(required=False, read_only=True)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = models.User
        validators = [
            EqualityValidator(
                fields=['password1', 'password2']
            ),
            LengthValidator('password1', 8),
            RegistrationAllowedValidator()
        ]
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'last_login', 'date_joined')

    def __init__(self, validate_non_fields=False, **kwargs):
        super(UserSerializer, self).__init__(**kwargs)
        self.validate_non_fields = validate_non_fields

    def validate_username(self, value):
        user = User.objects.filter(username=value)
        if user:
            raise ValidationError("Username needs to be unique.")
        return value

    def create(self, **kwargs):
        username = ''

        validated_username = self.validated_data['first_name'].lower() + '.' + self.validated_data['last_name'].lower()
        username_check = User.objects.filter(username=validated_username).count()

        if username_check == 0 and len(validated_username) <= settings.USERNAME_MAX_LENGTH:
            username = validated_username
        else:
            username = get_next_unique_id(User, 'username', validated_username)

            # check for max length for username
            if len(username) > settings.USERNAME_MAX_LENGTH:

                # check for max length for email
                if len(self.validated_data['email']) <= settings.USERNAME_MAX_LENGTH:
                    username = self.validated_data['email']
                else:
                    # generate random username
                    username = uuid.uuid4().hex[:settings.USERNAME_MAX_LENGTH]

        user = User.objects.create_user(username, self.validated_data.get('email'),
                                            self.initial_data.get('password1'))

        if not settings.EMAIL_ENABLED:
            user.is_active = 1

        user.first_name = self.validated_data['first_name']
        user.last_name = self.validated_data['last_name']
        user.save()
        user_profile = models.UserProfile()
        user_profile.user = user
        user_profile.save()

        if settings.EMAIL_ENABLED:
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            if isinstance(username, str):
                username = username.encode('utf-8')
            activation_key = hashlib.sha1(salt.encode('utf-8') + username).hexdigest()
            registration_model = models.RegistrationModel()
            registration_model.user = User.objects.get(id=user.id)
            registration_model.activation_key = activation_key
            # TODO self.context['request'] does not exist
            # send_activation_email(email=user.email, host=self.context['request'].get_host(),activation_key=activation_key)
            registration_model.save()
        return user

    def change_password(self):
        from django.contrib.auth import authenticate as auth_authenticate

        if 'password' not in self.initial_data:
            raise ValidationError("Current password needs to be provided")
        user = auth_authenticate(username=self.instance.username, password=self.initial_data['password'])
        if user is not None:
            self.instance.set_password(self.initial_data['password1'])
            self.instance.save()
        else:
            raise ValidationError("Username or password is incorrect.")

    def authenticate(self, request):
        from django.contrib.auth import authenticate as auth_authenticate

        # self.redirect_to = request.POST.get('next', '') #to be changed, POST does not contain any data

        username = request.data.get('username', '')
        password = request.data.get('password', '')

        email_or_username = username

        #match with username if not email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_or_username):
            username = email_or_username
        else:
            user = get_model_or_none(User, email=email_or_username)

            if user is not None:
                username = user.username

        user = auth_authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                oauth2_utils = Oauth2Utils()
                client = oauth2_utils.create_client(request, user)

                response_data = dict()
                response_data["client_id"] = client.client_id
                response_data["client_secret"] = client.client_secret
                response_data["username"] = user.username
                response_data["email"] = user.email
                response_data["first_name"] = user.first_name
                response_data["last_name"] = user.last_name
                response_data["date_joined"] = user.date_joined
                response_data["last_login"] = user.last_login

                return response_data, status.HTTP_201_CREATED
            else:
                raise AuthenticationFailed(_('Account is not activated yet.'))
        else:
            raise AuthenticationFailed(_('Username or password is incorrect.'))

    def change_username(self, **kwargs):
        from django.contrib.auth import authenticate as auth_authenticate

        if 'password' not in self.initial_data:
            raise ValidationError("Current password needs to be provided")
        if 'username' not in self.initial_data:
            raise ValidationError("New username needs to be provided")

        user = auth_authenticate(username=self.instance.username, password=self.initial_data['password'])

        if user is not None:
            self.instance.username = self.initial_data['username']
            self.instance.save()
        else:
            raise ValidationError("Username or password is incorrect.")