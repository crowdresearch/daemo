__author__ = 'dmorina'

from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from crowdsourcing.validators.utils import *
from csp import settings
class UserProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username',read_only=True)

    class Meta:
        model = models.UserProfile
        fields = ( 'user_username','gender', 'birthday', 'verified', 'address', 'nationality',
                  'picture', 'friends', 'roles', 'created_timestamp', 'deleted', 'languages')

        def create(self, validated_data):
            return Response({'status': 'BAD REQUEST'})
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

    def create(self, validated_data):
        username = ''
        username_check = User.objects.filter(username=validated_data['first_name'].lower()+'.'+validated_data['last_name'].lower())
        if not username_check:
            username = validated_data['first_name'].lower()+'.'+validated_data['last_name'].lower()
        else:
            #TODO username generating function
            username = validated_data['email']
        user = User.objects.create_user(username, validated_data.get('email'),validated_data.get('password1'))
        if not settings.EMAIL_ENABLED:
            user.is_active = 1
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.save()
        user_profile = models.UserProfile()
        user_profile.user = user
        user_profile.save()
        return user
    def is_valid_extended(self, raise_exception=False):
        if self.initial_data.get('email',None) is None:
            self.errors['email'] = 'Email cannot be empty.'
            return False
        if User.objects.filter(email__iexact=self.initial_data['email']):
            self.errors['email'] = 'Email already in use.'
            #if raise_exception:
            raise serializers.ValidationError("Email already in use.")
        return True
