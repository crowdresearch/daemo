__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
from django.db.models import Avg
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
    avg_rating = serializers.SerializerMethodField('average_rating')
    num_reviews = serializers.SerializerMethodField('number_reviews')
    def number_reviews(self,model):
        return model.modulereview_set.count()
    def average_rating(self, model):
        return model.modulerating_set.all().aggregate(Avg('value')) # should be updated automatically    
    class Meta:
        model = models.Module
        fields = ('id','name','owner','project','categories','keywords','status','price','repetition','module_timeout','deleted','created_timestamp','last_updated','avg_rating','num_reviews')
        read_only_fields = ('created_timestamp','last_updated','avg_rating')

class ModuleReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModuleReview
        fields = ('id','worker','annonymous','module','comments')
        read_only_fields = ('last_updated')

    def create(self, validated_data):
        try:
            Ncomments = validated_data.pop('comments')
            review = ModuleReview.all().get(**validated_data)
            review.comments = Ncomments
            review.save()
        except ObjectDoesNotExist:
            ModuleReview(**validated_data).save()

class ModuleRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModuleReview
        fields = ('id','worker','module','value')
        read_only_fields = ('last_updated')
    def create(self,validated_data):
        try:
            Nvalue = validated_data.pop('value')
            rating = ModuleReview.all().get(**validated_data)
            rating.value = Nvalue
            rating.save()
        except ObjectDoesNotExist:
            ModuleRating(**validated_data).save()



class WorkerModuleApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerModuleApplication


class QualificationApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification


class QualificationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QualificationItem
