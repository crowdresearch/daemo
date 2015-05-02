__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category

        fields = ('name','parent', 'deleted', 'last_updated', 'created_timestamp')

    def create(self, validated_data):
        return models.Project.objects.create(deleted=False, **validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.parent = validated_data.get('parent', instance.parent)
        instance.deleted = validated_data.get('deleted', False)
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

class ProjectSerializer(serializers.ModelSerializer):

    deleted = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.Project
        categories = CategorySerializer(many=True)

        fields = ( 'name','deadline', 'keywords', 'deleted', 'categories', 'last_updated', 'created_timestamp')

    def create(self, validated_data):
        return models.Project.objects.create(deleted=False, **validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.keywords = validated_data.get('keywords', instance.keywords)
        instance.deleted = validated_data.get('deleted', False)
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
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
