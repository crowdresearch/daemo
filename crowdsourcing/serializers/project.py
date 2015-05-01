__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ( 'name','deadline', 'keywords', 'deleted', 'categories', 'last_updated', 'created_timestamp')

        def create(self, validated_data):
            categories_data = validated_data.pop('categories')
            categories = models.ProjectCategory.objects.create(**categories_data)

            return models.UserProfile.objects.create(categories=categories, **validated_data)

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



class ProjectRequesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectRequester


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Module


class WorkerModuleApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerModuleApplication


class QualificationApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification


class QualificationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QualificationItem
