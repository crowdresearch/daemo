__author__ = 'elsabakiu, dmorina, neilthemathguy, megha, asmita'

from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.template import TemplateItemSerializer
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from rest_framework.exceptions import ValidationError
from django.db import transaction


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
    Good Lord, this needs cleanup :D
    '''
    num_tasks = serializers.SerializerMethodField()
    task_status_det = serializers.SerializerMethodField()
    task_category_det = serializers.SerializerMethodField()
    task_price_time = serializers.SerializerMethodField()
    total_balance = serializers.SerializerMethodField()
    class Meta:
        model = models.Worker
        fields = ('profile', 'skills', 'num_tasks', 'task_status_det', 'task_category_det', 'task_price_time', 'id','total_balance')
        read_only_fields = ('num_tasks', 'task_status_det', 'task_category_det', 'task_price_time','total_balance')

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

    # Returns tasks grouped by task status that the worker has undertaken
    # Also returns the number of tasks within each task status
    def get_task_status_det(self, instance):
        task_status = dict()
        number_task_per_status = dict()
        task_set = models.TaskWorker.objects.filter(worker=instance)

        # e.g. task_status = {'Accepted': ['Task1', 'Task2', 'Task3']}
        for task_worker in task_set:
            key = task_worker.task.module.status
            value = task_worker.task.module.description
            task_status.setdefault(key, [])
            task_status[key].append(value)

        # e.g. number_task_per_status = ['Accepted' : 3]
        for key_status in task_status:
            number_task_per_status[key_status] = len(task_status[key_status])

        return task_status, number_task_per_status

    # Returns the task grouped by Category that the worker has undertaken
    # Also returns the number of tasks within each category
    def get_task_category_det(self, instance):
        task_categories = dict()
        number_task_per_category = dict()
        task_set = models.TaskWorker.objects.filter(worker=instance)

        # e.g. task_categories = {'Image': ['Task1', 'Task2', 'Task3']}
        for task_worker in task_set:
            key = task_worker.task.module.categories.name
            value = task_worker.task.module.description
            task_categories.setdefault(key, [])
            task_categories[key].append(value)

        # e.g. number_task_per_category = ['Image' : 3]
        for key_category in task_categories:
            number_task_per_category[key_category] = len(task_categories[key_category])

        return task_categories, number_task_per_category

    # Returns the number of hours spent by a worker on the task and corresponding price
    def get_task_price_time(self, instance):
        task_det = []
        task_set = models.TaskWorker.objects.filter(worker=instance)
        # e.g. task_det = [{description: 'Task1', price: '50$', time_spent_in_hrs: '2', deadline: '2015-06-11'}]
        for task_worker in task_set:
            task_info = dict()
            deadline = task_worker.task.module.project.end_date
            # TODO(megha.agarwal): Refine duration spent on a task
            date1 = task_worker.task.created_timestamp
            date2 = task_worker.task.last_updated
            time_spent = (((date2 - date1).total_seconds()) / 3600)
            task_info['description'] = task_worker.task.module.description
            task_info['deadline'] = deadline
            task_info['price'] = task_worker.task.price
            task_info['time_spent_in_hrs'] = time_spent
            task_det.append(task_info)
        return task_det

    def get_total_balance(self,instance):
        acceptedresults = models.TaskWorkerResult.objects.all().filter(status = 2,task_worker__worker = instance)
        balance = 0
        for eachresult in acceptedresults:
            balance = balance + eachresult.task_worker.task.price
        return balance


class WorkerSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerSkill
        fields = ('worker', 'skill', 'level', 'verified', 'created_timestamp', 'last_updated')
        read_only_fields = ('worker', 'created_timestamp', 'last_updated', 'verified')

    def create(self, **kwargs):
        worker_skill = models.WorkerSkill.objects.get_or_create(worker=kwargs['worker'], **self.validated_data)
        return worker_skill


class TaskWorkerResultSerializer (serializers.ModelSerializer):
    #task_worker = TaskWorkerSerializer()
    template_item = TemplateItemSerializer()

    class Meta:
        model = models.TaskWorkerResult
        fields = ('template_item', 'result', 'status', 'created_timestamp', 'last_updated')
        read_only_fields = ('template_item', 'created_timestamp', 'last_updated')


class TaskWorkerSerializer (serializers.ModelSerializer):
    module = serializers.ModelField(model_field=models.Task()._meta.get_field('module'), write_only=True)
    task_worker_results = TaskWorkerResultSerializer(many=True, read_only=True)
    worker_alias = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskWorker
        fields = ('task', 'worker', 'created_timestamp', 'last_updated', 'module', 'task_worker_results', 'worker_alias')
        read_only_fields = ('task', 'worker', 'created_timestamp', 'last_updated')

    def create(self, **kwargs):
        module = self.validated_data.pop('module')
        module_instance = models.Module.objects.get(id=module)
        repetition = module_instance.repetition
        with transaction.atomic():
            tasks = models.Task.objects.select_for_update(nowait=False).filter(module=module).exclude(status__gt=2).exclude(task_workers__worker=kwargs['worker']).first()
            if tasks:
                task_worker = models.TaskWorker.objects.create(worker=kwargs['worker'], task=tasks)
                tasks.status = 2
                tasks.save()
                return task_worker
            else:
                raise ValidationError('No tasks left for this module')

    def get_worker_alias(self, obj):
        return obj.worker.profile.worker_alias



class WorkerModuleApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerModuleApplication
        fields = ('worker', 'module', 'status', 'created_timestamp', 'last_updated')
        read_only_fields = ('worker', 'module', 'created_timestamp', 'last_updated')
