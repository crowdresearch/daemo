__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
from django.db.models import Avg
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
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
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    class Meta:
        model = models.Project
        fields = ('id', 'name', 'start_date', 'end_date', 'description', 'keywords', 'deleted',
                  'categories')

    def create(self, validated_data):
        categories = validated_data.pop('categories')
        project = models.Project.objects.create(deleted=False, **validated_data)
        for c in categories:
            models.ProjectCategory.objects.create(project=project, category=c)
        return project

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
    avg_rating = serializers.SerializerMethodField()
    num_reviews = serializers.SerializerMethodField()
    deleted = serializers.BooleanField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all(), many=True)
    
    def create(self, validated_data):
        categories = validated_data.pop('categories')
        module = models.Module.objects.create(deleted = False,**validated_data)
        for c in categories:
            models.ModuleCategory.objects.create(module=module, category=c)
        return module

    def update(self,instance,validated_data):
        categories = validated_data.pop('categories')
        #for c in categories:
           #instance.ModuleCategory.objects.create(module=module, category=c)
        instance.name = validated_data.get('name', instance.name)
        instance.keywords = validated_data.get('keywords', instance.keywords)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price',instance.price)
        instance.repetition = validated_data.get('repetition',instance.repetition)
        instance.module_timeout = validated_data.get('module_timeout',instance.module_timeout)
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

    def get_num_reviews(self,model):
        return model.modulereview_set.count()

    def get_avg_rating(self, model):
        return model.modulerating_set.all().aggregate(Avg('value')) # should be updated automatically 

    class Meta:
        model = models.Module
        fields = ('id', 'name', 'owner', 'project', 'categories', 'description', 'keywords', 'status',
                  'price','repetition','module_timeout','deleted','created_timestamp','last_updated','avg_rating','num_reviews')
        read_only_fields = ('created_timestamp','last_updated','avg_rating')

class ModuleReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModuleReview
        fields = ('id','worker','annonymous','module','comments')
        read_only_fields = ('last_updated')


class ModuleRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModuleRating
        fields = ('id','worker','module','value')
        read_only_fields = ('last_updated')

    


class WorkerModuleApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerModuleApplication


class QualificationApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification


class QualificationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QualificationItem
