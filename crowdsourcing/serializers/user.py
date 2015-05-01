__author__ = 'dmorina'

from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json


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
    class Meta:
        model = models.User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_superuser', 'is_staff', 'last_login', 'date_joined')
