from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skill
        fields = ('name', 'description', 'verified', 'deleted', 'created_timestamp', 'last_updated', 'id')
        read_only_fields = ('created_timestamp', 'last_updated')

    def create(self, validated_data):
        skill = models.Skill.objects.create(deleted=False, **validated_data)
        return skill

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        # TODO(megha.agarwal): Define method to verify the skill added
        instance.verified = True
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance


class WorkerSerializer(DynamicFieldsModelSerializer):
    '''
    Good Lord, this needs cleanup :D, yes it really does
    '''
    num_tasks = serializers.SerializerMethodField()

    class Meta:
        model = models.Worker
        fields = ('profile', 'skills', 'num_tasks', 'id',)
        read_only_fields = ('num_tasks',)

    def create(self, validated_data):
        worker = models.Worker.objects.create(**validated_data)
        return worker

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

    # Returns number of tasks the worker has/had worked on
    def get_num_tasks(self, instance):
        # response_data = models.Worker.objects.filter(taskworker__worker = instance).count()
        response_data = models.TaskWorker.objects.filter(worker=instance).count()
        return response_data


class WorkerSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerSkill
        fields = ('worker', 'skill', 'level', 'verified', 'created_timestamp', 'last_updated')
        read_only_fields = ('worker', 'created_timestamp', 'last_updated', 'verified')

    def create(self, **kwargs):
        worker_skill = models.WorkerSkill.objects.get_or_create(worker=kwargs['worker'], **self.validated_data)
        return worker_skill
