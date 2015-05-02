__author__ = 'dmorina'

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
from crowdsourcing.utils import get_model_or_none, Oauth2Utils
from rest_framework import status

class UserProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username',read_only=True)

    class Meta:
        model = models.UserProfile
        fields = ( 'user_username','gender', 'birthday', 'verified', 'address', 'nationality',
                  'picture', 'friends', 'roles', 'created_timestamp', 'deleted', 'languages')

        def create(self, validated_data):
            address_data = validated_data.pop('address')
            address = models.Address.objects.create(**address_data)

            return models.UserProfile.objects.create(address=address, **validated_data)

        def update(self, instance, validated_data):
            address = instance.address
            address_data = validated_data.pop('address')

            address.city = address_data.get('city', address.city)
            address.country = address_data.get('country', address.country)
            address.last_updated = datetime.now()
            address.street = address_data.get('street', address.street)

            address.save()

            instance.gender = validated_data.get('gender', instance.gender)
            instance.birthday = validated_data.get('birthday', instance.birthday)
            instance.verified = validated_data.get('verified', instance.verified)
            instance.picture = validated_data.get('picture', instance.picture)
            instance.save(address=address)
            return instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = {'id','name'}


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserRole


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Friendship


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserPreferences


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
                fields = ['password1', 'password2']
            ),
            LengthValidator('password1', 8),
            RegistrationAllowedValidator()
        ]
        fields = ('id', 'username','first_name', 'last_name', 'email',
                  'is_superuser', 'is_staff', 'last_login', 'date_joined')


    def create(self, **kwargs):
        username = ''
        username_check = User.objects.filter(username=self.validated_data['first_name'].lower()+'.'+self.validated_data['last_name'].lower())
        if not username_check:
            username = self.validated_data['first_name'].lower()+'.'+self.validated_data['last_name'].lower()
        else:
            #TODO username generating function
            username = self.validated_data['email']
        user = User.objects.create_user(username, self.validated_data.get('email'), self.initial_data.get('password1'))
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
            activation_key = hashlib.sha1(salt.encode('utf-8')+username).hexdigest()
            registration_model = models.RegistrationModel()
            registration_model.user = User.objects.get(id=user.id)
            registration_model.activation_key = activation_key
            #TODO self.context['request'] does not exist
            #send_activation_email(email=user.email, host=self.context['request'].get_host(),activation_key=activation_key)
            registration_model.save()
        return user

    def change_password(self):
        self.instance.set_password(self.initial_data['password1'])
        self.instance.save()

    def authenticate(self, request):
        from django.contrib.auth import authenticate as auth_authenticate
        #self.redirect_to = request.POST.get('next', '') #to be changed, POST does not contain any data
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        email_or_username = username
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_or_username):
            username = email_or_username
        else:
            user = get_model_or_none(User,email=email_or_username)
            if user is not None:
                username = user.username

        user = auth_authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                oauth2_utils = Oauth2Utils()
                client = oauth2_utils.create_client(request,user)
                response_data = {}
                response_data["client_id"] = client.client_id
                response_data["client_secret"] = client.client_secret
                response_data["username"] = user.username
                response_data["email"] = user.email
                response_data["first_name"] = user.first_name
                response_data["last_name"] = user.last_name
                response_data["date_joined"] = user.date_joined
                response_data["last_login"] = user.last_login
                return response_data, status.HTTP_201_CREATED
                #return Response(response_data,status=status.HTTP_201_CREATED)
            else:
                return {
                    'status': 'Unauthorized',
                    'message': 'Account is not activated yet.'
                }, status.HTTP_401_UNAUTHORIZED
        else:
            return {
            'status': 'Unauthorized',
            'message': 'Username or password is incorrect.'
        }, status.HTTP_401_UNAUTHORIZED
