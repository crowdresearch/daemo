__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json


class CategorySerializer(serializers.ModelSerializer):

    deleted = serializers.BooleanField(read_only=True)
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'parent', 'deleted')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.parent = validated_data.get('parent', instance.parent)
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

class ProjectSerializer(serializers.ModelSerializer):

    deleted = serializers.BooleanField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all(), many=True)

    class Meta:
        model = models.Project
        fields = ('id', 'name','deadline', 'keywords', 'deleted', 'categories')

    def create(self, validated_data):
        categories = validated_data.pop('categories')
        project = models.Project.objects.create(deleted=False, **validated_data)
        for c in categories:
            models.ProjectCategory.objects.create(project=project, category=c)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.keywords = validated_data.get('keywords', instance.keywords)
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
