__author__ = 'elsabakiu, dmorina, neilthemathguy, megha, asmita'

from crowdsourcing import models
from rest_framework import serializers, status
from datetime import datetime

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skill
        fields = ('name', 'description', 'verified', 'deleted', 'created_timestamp', 'last_updated')
        read_only_fields = ('created_timestamp', 'last_updated')

    def create(self, validated_data):
        skill = models.Skill.objects.create(deleted=False, **validated_data)
        return skill

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        #TODO(megha.agarwal): Define method to verify the skill added
        instance.verified = True
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance


#Return difference between start_date and end_date in hours
def date_diff_inHours (start_date, end_date):
    date1 = datetime.strptime(start_date, "%Y-%m-%d")
    date2 = datetime.strptime(end_date, "%Y-%m-%d")
    return abs((date1 - date2).hour)


class WorkerSerializer(serializers.ModelSerializer):
    num_tasks = serializers.SerializerMethodField()
    task_status_det = serializers.SerializerMethodField()
    task_category_det = serializers.SerializerMethodField()
    task_price_time = serializers.SerializerMethodField()

    class Meta:
        model = models.Worker
        fields = ('profile', 'skills', 'num_tasks', 'task_status_det', 'task_category_det', 'task_price_time')
        read_only_fields = ('num_tasks', 'task_status_det', 'task_category_det', 'task_price_time')

    def create(self, validated_data):
        skill_set = validated_data.pop('skills')
        worker = models.Worker.objects.create(deleted=False, **validated_data)
        for get_skill in skill_set:
            models.WorkerSkill.objects.create(worker = worker, skill = get_skill)
        return worker

    # Returns number of tasks the worker has/had worked on
    def get_num_tasks(self):
        taskWorker = models.TaskWorker()
        response_data = taskWorker.objects.filter(worker = self).count()
        return response_data

    # Returns tasks grouped by task status that the worker has undertaken
    # Also returns the number of tasks within each task status
    def get_task_status_det(self):
        task_status = dict()
        number_task_per_status = dict()
        taskWorker = models.TaskWorker()
        task_set =  taskWorker.objects.filter(worker = self)

        # e.g. task_status = {'Accepted': ['Task1', 'Task2', 'Task3']}
        for task in task_set:
            key = task.module.statuses
            value = task.module.description
            task_status.setdefault(key, [])
            task_status[key].append(value)

        # e.g. number_task_per_status = ['Accepted' : 3]
        for key_status in task_status:
            number_task_per_status[key_status] = len(task_status[key_status])

        return task_status, number_task_per_status

    # Returns the task grouped by Category that the worker has undertaken
    # Also returns the number of tasks within each category
    def get_task_category_det(self):
        task_categories = dict()
        number_task_per_category = dict()
        taskWorker = models.TaskWorker()
        task_set = taskWorker.objects.filter(worker = self)

        # e.g. task_categories = {'Image': ['Task1', 'Task2', 'Task3']}
        for task in task_set:
            key = task.module.categories.caregory.name
            value = task.module.description
            task_categories.setdefault(key, [])
            task_categories[key].append(value)

        # e.g. number_task_per_category = ['Image' : 3]
        for key_category in task_categories:
            number_task_per_category[key_category] = len(task_categories[key_category])

        return task_categories, number_task_per_category

    #Returns the number of hours spent by a worker on the task and corresponding price
    def get_task_price_time(self):
        task_det = []
        taskWorker = models.TaskWorker()
        task_set = taskWorker.objects.filter(worker = self)
        # e.g. task_det = [{description: 'Task1', price: '50$', time_spent_in_hrs: '2', deadline: '2015-06-11'}]
        for task in task_set:
            task_info = dict()
            deadline = task.module.project.deadline
            #TODO(megha.agarwal): Refine duration spent on a task
            time_spent = date_diff_inHours (task.created_timestamp - task.last_updated)
            task_info['description'] = task.module.description
            task_info['deadline'] = deadline
            task_info['price'] = task.module.price
            task_info['time_spent_in_hrs'] = time_spent
            task_det.append(task_info)
        return task_det


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