__author__ = 'elsabakiu, asmita, megha,kajal'

from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.worker import TaskWorkerSerializer

class TaskSerializer(serializers.ModelSerializer):
    task_workers = TaskWorkerSerializer(many=True, read_only=True)

    def create(self, **kwargs):
        task = models.Task.objects.create(**self.validated_data)
        return task

    def update(self, instance, validated_data):
        module = validated_data.pop('module')
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

    class Meta:
        model = models.Task
        fields = ('module','status', 'deleted', 'created_timestamp', 'last_updated', 'data', 'task_workers')
        read_only_fields = ('created_timestamp', 'last_updated', 'deleted')


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ('name', 'iso_code', 'last_updated')
        read_only_fields = ('last_updated')