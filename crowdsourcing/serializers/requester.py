__author__ = 'elsabakiu, asmita, megha'

from crowdsourcing import models
from rest_framework import serializers
import datetime

class RequesterSerializer(serializers.ModelSerializer):
    total_projects = serializers.SerializerMethodField()
    current_projects = serializers.SerializerMethodField()
    waiting_projects = serializers.SerializerMethodField()
    upcoming_deadline = serializers.SerializerMethodField()

    def get_total_projects(self, model):
        return model.project_set.count()

    def get_current_projects(self, model):
        return models.Module.objects.all().filter(project = model, status = 3, deleted = False).distinct('project')

    def get_waiting_projects(self, model):
        return models.Module.objects.all().filter(project = model, status = 2, deleted = False).distinct('project')

    def get_upcoming_deadline(self, model):
        return models.Module.objects.all().filter(deadline__gt = datetime.datetime.now().date()).aggregate(deadline = Min('deadline')).get('deadline')

    def get_active_tasks(self, model):
        return 0

    def get_recently_approved(self, model):
        return 0

    class Meta:
        model = models.Requester
        fields = ('id','profile','total_projects','current_projects','waiting_projects','upcoming_deadline')
        read_only_fields = ('id','total_projects','current_projects','waiting_projects','upcoming_deadline')


class RequesterRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RequesterRanking


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification
        fields = ('module', 'types', 'type', 'created_timestamp', 'last_updated')
        read_only_fields = ('module', 'types', 'created_timestamp', 'last_updated')
