__author__ = 'elsabakiu, asmita, megha'

from crowdsourcing import models
from rest_framework import serializers
import datetime

class RequesterSerializer(serializers.ModelSerializer):
    total_projects = serializers.SerializerMethodField()
    current_projects = serializers.SerializerMethodField()
    waiting_projects = serializers.SerializerMethodField()

    def get_total_projects(self, model):
        #TODO : also show count of projects, in which requester is collaborator
        return model.project_set.count()

    def get_current_projects(self, model):
        #TODO : also show count of projects, in which requester is collaborator
        return models.Module.objects.all().filter(project__owner = model, status = 3, deleted = False).distinct('project').count()

    def get_waiting_projects(self, model):
        #TODO : also show count of projects, in which requester is collaborator
        return models.Module.objects.all().filter(project__owner = model, status = 2, deleted = False).distinct('project').count()

    class Meta:
        model = models.Requester
        fields = ('id','profile','total_projects','current_projects','waiting_projects')
        read_only_fields = ('id','total_projects','current_projects','waiting_projects')


class RequesterRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RequesterRanking


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification
        fields = ('module', 'types', 'type', 'created_timestamp', 'last_updated')
        read_only_fields = ('module', 'types', 'created_timestamp', 'last_updated')
