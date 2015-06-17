__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
from django.db.models import Avg
from django.db.models import Max
from django.db.models import Min
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
import json


class CategorySerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = models.Category
        fields = ('id', 'name', 'parent')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.parent = validated_data.get('parent', instance.parent)
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

class ProjectSerializer(DynamicFieldsModelSerializer):

    deleted = serializers.BooleanField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all(), many=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    class Meta:
        model = models.Project
        fields = ('id','owner', 'name', 'start_date', 'end_date', 'description', 'keywords', 'deleted',
                  'categories')

    def create(self, **kwargs):
        categories = self.validated_data.pop('categories')
        project = models.Project.objects.create(owner=kwargs['owner'],deleted=False, **self.validated_data)
        #for c in categories:
        #    models.ProjectCategory.objects.create(project=project, category=c)
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


class ModuleSerializer(DynamicFieldsModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    num_reviews = serializers.SerializerMethodField()
    num_raters = serializers.SerializerMethodField()
    avg_pay = serializers.SerializerMethodField()
    min_pay = serializers.SerializerMethodField()
    completed_on = serializers.SerializerMethodField()
    total_submissions = serializers.SerializerMethodField()
    num_contributors = serializers.SerializerMethodField()
    num_accepted = serializers.SerializerMethodField()
    num_rejected = serializers.SerializerMethodField()
    total_tasks = serializers.SerializerMethodField()

    deleted = serializers.BooleanField(read_only=True)
    # categories = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all(), many=True)
    categories = CategorySerializer(many=True,read_only=True,fields=('id','name'))
    project = ProjectSerializer(many = False,read_only = True,fields=('id','name'))
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

    def get_num_raters(self,model):
        return model.modulerating_set.count()

    def get_avg_rating(self, model):
        return model.modulerating_set.all().aggregate(avg=Avg('value')).get('avg') # should be updated automatically 

    def get_avg_pay(self, model):
        return model.task_set.all().aggregate(avg=Avg('price')).get('avg') 
    
    def get_min_pay(self, model):
        return model.task_set.all().aggregate(min=Min('price')).get('min') # should be updated automatically 

    def get_num_accepted(self, model):
        return models.TaskWorkerResult.objects.all().filter(task_worker__task__module = model,status = 2).count();      

    def get_num_rejected(self, model):
        return models.TaskWorkerResult.objects.all().filter(task_worker__task__module = model,status = 3).count();      
    
    def get_total_tasks(self, model):
        return model.task_set.all().count();      


    def get_completed_on(self, model):
        if(model.task_set.all().exclude(status = 4).count()>0):
            return "Not Comlpeted"
        else:
            return model.task_set.all().aggregate(date=Max('last_updated')).get('date').date()

    def get_total_submissions(self,model):
        return models.TaskWorkerResult.objects.all().filter(task_worker__task__module = model).count();      

    def get_num_contributors(self,model):
        acceptedTaskWorker = models.TaskWorker.objects.all().filter(task__module = model,taskworkerresult__status = 2);
        return acceptedTaskWorker.order_by('worker').distinct('worker').count()

    class Meta:
        model = models.Module
        fields = ('id', 'name', 'owner', 'project', 'categories', 'description', 'keywords', 'status',
                  'repetition','module_timeout','deleted','created_timestamp','last_updated','avg_rating','num_reviews','completed_on','total_submissions','num_contributors','num_raters','min_pay','avg_pay','num_accepted','num_rejected','total_tasks')
        read_only_fields = ('created_timestamp','last_updated')

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
