__author__ = ['elsabakiu', 'dmorina', 'neilthemathguy', 'megha']

from crowdsourcing import models
from rest_framework import serializers

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Worker
        fields = ('profile')
        read_only_fields = ('profile')


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skill
        fields = ('name', 'description', 'verified', 'deleted', 'created_timestamp', 'last_updated')
        read_only_fields = ('created_timestamp', 'last_updated')


class WorkerSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerSkill
        fields = ('worker', 'skill', 'level', 'verified', 'created_timestamp', 'last_updated')
        read_only_fields = ('worker', 'created_timestamp', 'last_updated')


class TaskWorkerSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.TaskWorker
        fields = ('task', 'worker', 'created_timestamp', 'last_updated')
        read_only_fields = ('task', 'worker', 'created_timestamp', 'last_updated')


class TaskWorkerResultSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.TaskWorkerResult
        fields = ('task_worker', 'template_item', 'status', 'created_timestamp', 'last_updated')
        read_only_fields = ('task_worker', 'template_item', 'created_timestamp', 'last_updated')


class WorkerModuleApplicationSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.WorkerModuleApplication
        fields = ('worker', 'module', 'status', 'created_timestamp', 'last_updated')
        read_only_fields = ('worker', 'module', 'created_timestamp', 'last_updated')