__author__ = 'elsabakiu, asmita, megha,kajal'

from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.serializers.template import TemplateItemSerializer
from rest_framework.exceptions import ValidationError
from django.db import transaction
from crowdsourcing.serializers.template import TemplateSerializer
import json

class TaskWorkerResultSerializer (serializers.ModelSerializer):
    #task_worker = TaskWorkerSerializer()
    template_item = TemplateItemSerializer()

    class Meta:
        model = models.TaskWorkerResult
        fields = ('id', 'template_item', 'result', 'status', 'created_timestamp', 'last_updated')
        read_only_fields = ('template_item', 'created_timestamp', 'last_updated')


class TaskWorkerSerializer (serializers.ModelSerializer):
    task_worker_results = TaskWorkerResultSerializer(many=True, read_only=True)
    worker_alias = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskWorker
        fields = ('id','task', 'worker', 'created_timestamp', 'last_updated', 'task_worker_results', 'worker_alias')
        read_only_fields = ('task', 'worker', 'created_timestamp', 'last_updated')

    def create(self, **kwargs):
        module = self.initial_data.pop('module')
        module_instance = models.Module.objects.get(id=module)
        repetition = module_instance.repetition
        with transaction.atomic(): # TODO include repetition in the allocation
            tasks = models.Task.objects.select_for_update(nowait=False).filter(module=module)\
                .exclude(status__gt=2).exclude(task_workers__worker=kwargs['worker']).first()
            if tasks:
                task_worker = models.TaskWorker.objects.create(worker=kwargs['worker'], task=tasks)
                tasks.status = 2
                tasks.save()
                return task_worker
            else:
                raise ValidationError('No tasks left for this module')

    def get_worker_alias(self, obj):
        return obj.worker.alias


class TaskSerializer(DynamicFieldsModelSerializer):
    task_workers = TaskWorkerSerializer(many=True, read_only=True)
    task_template = serializers.SerializerMethodField()

    class Meta:
        model = models.Task
        fields = ('id', 'module', 'status', 'deleted', 'created_timestamp', 'last_updated', 'data',
                  'task_workers', 'task_template')
        read_only_fields = ('created_timestamp', 'last_updated', 'deleted')

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

    def get_task_template(self, obj):
        template = TemplateSerializer(instance=obj.module.template, many=True).data[0]
        data = json.loads(obj.data)
        for item in template['template_items']:
            if item['data_source'] is not None and item['data_source'] in data:
                item['values'] = data[item['data_source']]
        return template


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ('name', 'iso_code', 'last_updated')
        read_only_fields = ('last_updated')