from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.serializers.template import TemplateItemSerializer
from rest_framework.exceptions import ValidationError
from django.db import transaction
from crowdsourcing.serializers.template import TemplateSerializer
import json
from django.db.models import Count, F


class TaskWorkerResultListSerializer(serializers.ListSerializer):
    def create(self, **kwargs):
        for item in self.validated_data:
            models.TaskWorkerResult.objects.get_or_create(task_worker=kwargs['task_worker'], **item)


class TaskWorkerResultSerializer(DynamicFieldsModelSerializer):
    template_item_id = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskWorkerResult
        list_serializer_class = TaskWorkerResultListSerializer
        fields = ('id', 'template_item', 'result', 'status', 'created_timestamp', 'last_updated', 'template_item_id')
        read_only_fields = ('created_timestamp', 'last_updated')

    def create(self, **kwargs):
        models.TaskWorkerResult.objects.get_or_create(self.validated_data)

    def get_template_item_id(self, obj):
        template_item = TemplateItemSerializer(instance=obj.template_item).data
        return template_item['id']


class TaskWorkerSerializer(DynamicFieldsModelSerializer):
    import multiprocessing
    
    lock = multiprocessing.Lock()
    task_worker_results = TaskWorkerResultSerializer(many=True, read_only=True)
    worker_alias = serializers.SerializerMethodField()
    task_worker_results_monitoring = serializers.SerializerMethodField()
    updated_delta = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskWorker
        fields = ('id', 'task', 'worker', 'task_status', 'created_timestamp', 'last_updated',
                  'task_worker_results', 'worker_alias', 'task_worker_results_monitoring', 'updated_delta')
        read_only_fields = ('task', 'worker', 'created_timestamp', 'last_updated')

    def create(self, **kwargs):
        module = kwargs['module']
        module_instance = models.Module.objects.get(id=module)
        repetition = module_instance.repetition
        with self.lock:
            with transaction.atomic(): # select_for_update(nowait=False)
                tasks = models.Task.objects.filter(module=module).exclude(
                    task_workers__worker=kwargs['worker']) \
                    .annotate(task_worker_count=Count('task_workers')) \
                    .filter(module__repetition__gt=F('task_worker_count')).first()
                if not tasks:
                    tasks = models.Task.objects.filter(module=module) \
                        .exclude(task_workers__worker=kwargs['worker'], task_workers__task_status=6) \
                        .annotate(task_worker_count=Count('task_workers')) \
                        .filter(module__repetition__gt=F('task_worker_count')).first()
                if tasks:
                    task_worker = models.TaskWorker.objects.create(worker=kwargs['worker'], task=tasks)
                    tasks.status = 2
                    tasks.save()
                    return task_worker
                else:
                    raise ValidationError('No tasks left for this module')

    def get_worker_alias(self, obj):
        return obj.worker.alias

    def get_updated_delta(self, obj):
        from crowdsourcing.utils import get_time_delta

        return get_time_delta(obj.last_updated)

    def get_task_worker_results_monitoring(self, obj):
        task_worker_results = TaskWorkerResultSerializer(instance=obj.task_worker_results, many=True,
                                                         fields=('template_item_id', 'result')).data
        return task_worker_results


class TaskSerializer(DynamicFieldsModelSerializer):
    task_workers = TaskWorkerSerializer(many=True, read_only=True)
    task_workers_monitoring = serializers.SerializerMethodField()
    task_template = serializers.SerializerMethodField()
    template_items_monitoring = serializers.SerializerMethodField()

    class Meta:
        model = models.Task
        fields = ('id', 'module', 'status', 'deleted', 'created_timestamp', 'last_updated', 'data',
                  'task_workers', 'task_workers_monitoring', 'task_template', 'template_items_monitoring')
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

    def get_task_template(self, obj, return_type='full'):
        template = None
        if return_type == 'full':
            template = TemplateSerializer(instance=obj.module.template, many=True).data[0]
        else:
            template = \
            TemplateSerializer(instance=obj.module.template, many=True, fields=('id', 'template_items')).data[0]
        data = json.loads(obj.data)
        for item in template['template_items']:
            if item['data_source'] is not None and item['data_source'] in data:
                item['values'] = data[item['data_source']]
        template['template_items'] = sorted(template['template_items'], key=lambda k: k['id'])
        return template

    def get_template_items_monitoring(self, obj):
        return TemplateItemSerializer(instance=self.get_task_template(obj, 'partial')['template_items'], many=True,
                                      fields=('id', 'role', 'values', 'data_source')).data

    def get_task_workers_monitoring(self, obj):
        skipped = 6
        task_workers_filtered = obj.task_workers.exclude(task_status=skipped)
        task_workers = TaskWorkerSerializer(instance=task_workers_filtered, many=True,
                                            fields=('id', 'task_status', 'worker_alias',
                                                    'task_worker_results_monitoring', 'updated_delta')).data
        return task_workers


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ('name', 'iso_code', 'last_updated')
        read_only_fields = ('last_updated')
