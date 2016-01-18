from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.serializers.template import TemplateItemSerializer
from django.db import transaction
from crowdsourcing.serializers.template import TemplateSerializer
from crowdsourcing.serializers.message import CommentSerializer
import ast


class TaskWorkerResultListSerializer(serializers.ListSerializer):
    def create(self, **kwargs):
        for item in self.validated_data:
            models.TaskWorkerResult.objects.get_or_create(task_worker=kwargs['task_worker'], **item)

    def update(self, instances, validated_data):
        for instance in instances:
            for item in validated_data:
                if instance.template_item.id == item.get('template_item').id:
                    instance.result = item.get('result', instance.result)
                    instance.save()
                    break


class TaskWorkerResultSerializer(DynamicFieldsModelSerializer):
    template_item_id = serializers.SerializerMethodField()
    result = serializers.JSONField(allow_null=True)

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
    requester_alias = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    task_template = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskWorker
        fields = ('id', 'task', 'worker', 'task_status', 'created_timestamp', 'last_updated',
                  'task_worker_results', 'worker_alias', 'task_worker_results_monitoring', 'updated_delta',
                  'requester_alias', 'project', 'task_template', 'is_paid', 'has_comments')
        read_only_fields = ('task', 'worker', 'created_timestamp', 'last_updated', 'has_comments')

    def create(self, **kwargs):
        project = kwargs['project']
        skipped = False
        task_worker = {}
        with self.lock:
            with transaction.atomic():  # select_for_update(nowait=False)
                query = '''SELECT
                      "crowdsourcing_task"."id",
                      "crowdsourcing_task"."project_id",
                      "crowdsourcing_task"."status",
                      "crowdsourcing_task"."data",
                      "crowdsourcing_task"."deleted",
                      "crowdsourcing_task"."created_timestamp",
                      "crowdsourcing_task"."last_updated",
                      "crowdsourcing_task"."price"
                    FROM "crowdsourcing_task"
                      INNER JOIN "crowdsourcing_project"
                        ON ("crowdsourcing_task"."project_id"="crowdsourcing_project"."id")
                      LEFT OUTER JOIN "crowdsourcing_taskworker" ON (
                      "crowdsourcing_task"."id" = "crowdsourcing_taskworker"."task_id"
                      and crowdsourcing_taskworker.task_status not in (4,6)
                      )
                    WHERE ("crowdsourcing_task"."project_id" = %s)
                    GROUP BY "crowdsourcing_task"."id", "crowdsourcing_task"."project_id",
                        "crowdsourcing_task"."status", "crowdsourcing_task"."data",
                        "crowdsourcing_task"."deleted",
                       "crowdsourcing_task"."created_timestamp",
                      "crowdsourcing_task"."last_updated", "crowdsourcing_task"."price",
                      "crowdsourcing_project"."repetition", crowdsourcing_taskworker.task_id
                    HAVING "crowdsourcing_project"."repetition" > (COUNT("crowdsourcing_taskworker"."id"))
                    and "crowdsourcing_task"."id" not in (select "crowdsourcing_taskworker"."task_id"
                    from "crowdsourcing_taskworker"
                    where "crowdsourcing_taskworker"."worker_id"=%s) LIMIT 1'''

                tasks = models.Task.objects.raw(query, params=[project, kwargs['worker'].id])

                if not len(list(tasks)):
                    tasks = models.Task.objects.raw(
                        '''
                        SELECT
                          "crowdsourcing_task"."id",
                          "crowdsourcing_task"."project_id",
                          "crowdsourcing_task"."status",
                          "crowdsourcing_task"."data",
                          "crowdsourcing_task"."deleted",
                          "crowdsourcing_task"."created_timestamp",
                          "crowdsourcing_task"."last_updated",
                          "crowdsourcing_task"."price"
                        FROM "crowdsourcing_task"
                          INNER JOIN "crowdsourcing_project"
                          ON ("crowdsourcing_task"."project_id" = "crowdsourcing_project"."id")
                          LEFT OUTER JOIN "crowdsourcing_taskworker"
                          ON ("crowdsourcing_task"."id" = "crowdsourcing_taskworker"."task_id"
                          and crowdsourcing_taskworker.task_status not in (4,6))
                        WHERE ("crowdsourcing_task"."project_id" = %s)
                        GROUP BY "crowdsourcing_task"."id", "crowdsourcing_task"."project_id",
                          "crowdsourcing_task"."status",
                          "crowdsourcing_task"."data", "crowdsourcing_task"."deleted",
                          "crowdsourcing_task"."created_timestamp",
                          "crowdsourcing_task"."last_updated", "crowdsourcing_task"."price",
                          "crowdsourcing_project"."repetition", crowdsourcing_taskworker.task_id
                        HAVING "crowdsourcing_project"."repetition" > (COUNT("crowdsourcing_taskworker"."id"))
                        and crowdsourcing_task.id in (select crowdsourcing_taskworker.task_id from
                        crowdsourcing_taskworker where worker_id=%s and task_status=6) order by random()
                        ''', params=[project, kwargs['worker'].id])
                    skipped = True
                if len(list(tasks)) and not skipped:
                    task_worker = models.TaskWorker.objects.create(worker=kwargs['worker'], task=tasks[0])
                elif len(list(tasks)) and skipped:
                    task_worker = models.TaskWorker.objects.get(worker=kwargs['worker'], task=tasks[0])
                    task_worker.task_status = 1
                    task_worker.save()
                else:
                    return {}, 204
                return task_worker, 200

    def get_worker_alias(self, obj):
        return obj.worker.alias

    def get_updated_delta(self, obj):
        from crowdsourcing.utils import get_time_delta

        return get_time_delta(obj.last_updated)

    def get_task_worker_results_monitoring(self, obj):
        task_worker_results = TaskWorkerResultSerializer(instance=obj.task_worker_results, many=True,
                                                         fields=('template_item_id', 'result')).data
        return task_worker_results

    def get_requester_alias(self, obj):
        return obj.task.project.owner.alias

    def get_project(self, obj):
        return {'id': obj.task.project.id, 'name': obj.task.project.name, 'price': obj.task.project.price}

    def get_task_template(self, obj):
        task = TaskSerializer(instance=obj.task, fields=('id', 'task_template')).data
        template = task['task_template']
        task_worker_results = TaskWorkerResultSerializer(instance=obj.task_worker_results, many=True,
                                                         fields=('template_item_id', 'result')).data
        for task_worker_result in task_worker_results:
            for item in template['template_items']:
                if task_worker_result['template_item_id'] == item['id'] and item['role'] == 'input' and \
                        task_worker_result['result'] is not None:
                    if item['type'] == 'checkbox':
                        item['aux_attributes']['options'] = task_worker_result['result']
                    else:
                        item['answer'] = task_worker_result['result']

        template['template_items'] = sorted(template['template_items'], key=lambda k: k['position'])

        return template

    def get_has_comments(self, obj):
        return obj.task.taskcomment_task.count() > 0


class TaskCommentSerializer(DynamicFieldsModelSerializer):
    comment = CommentSerializer()

    class Meta:
        model = models.TaskComment
        fields = ('id', 'task', 'comment')
        read_only_fields = ('task',)

    def create(self, **kwargs):
        comment_data = self.validated_data.pop('comment')
        comment_serializer = CommentSerializer(data=comment_data)
        if comment_serializer.is_valid():
            comment = comment_serializer.create(sender=kwargs['sender'])
            task_comment = models.TaskComment.objects.create(task_id=kwargs['task'], comment_id=comment.id)
            return {'id': task_comment.id, 'comment': comment}


class TaskSerializer(DynamicFieldsModelSerializer):
    task_workers = TaskWorkerSerializer(many=True, read_only=True)
    task_workers_monitoring = serializers.SerializerMethodField()
    task_template = serializers.SerializerMethodField()
    template_items_monitoring = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()
    project_data = serializers.SerializerMethodField()
    comments = TaskCommentSerializer(many=True, source='taskcomment_task', read_only=True)
    task_workers_for_download = serializers.SerializerMethodField()

    class Meta:
        model = models.Task
        fields = ('id', 'project', 'status', 'deleted', 'created_timestamp', 'last_updated', 'data',
                  'task_workers', 'task_workers_monitoring', 'task_template', 'template_items_monitoring',
                  'has_comments', 'comments', 'project_data', 'task_workers_for_download')
        read_only_fields = ('created_timestamp', 'last_updated', 'deleted', 'has_comments', 'comments', 'project_data')

    def create(self, **kwargs):
        task = models.Task.objects.create(**self.validated_data)
        return task

    def update(self, instance, validated_data):
        validated_data.pop('project')
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
            template = TemplateSerializer(instance=obj.project.templates, many=True).data[0]
        else:
            template = \
                TemplateSerializer(instance=obj.project.templates, many=True, fields=('id', 'template_items')).data[0]
        data = ast.literal_eval(obj.data)
        for item in template['template_items']:
            aux_attrib = item['aux_attributes']
            if 'data_source' in aux_attrib and aux_attrib['data_source'] is not None and \
                    aux_attrib['data_source'] in data and 'src' in aux_attrib:
                aux_attrib['src'] = data[aux_attrib['data_source']]
            if 'question' in aux_attrib and 'data_source' in aux_attrib['question'] and \
                    aux_attrib['question']['data_source'] is not None and \
                    aux_attrib['question']['data_source'] in data:
                aux_attrib['question']['value'] = data[aux_attrib['question']['data_source']]
            if 'options' in aux_attrib:
                for option in aux_attrib['options']:
                    if 'data_source' in option and option['data_source'] is not None and option['data_source'] in data:
                        option['value'] = data[option['data_source']]

        template['template_items'] = sorted(template['template_items'], key=lambda k: k['position'])
        return template

    def get_template_items_monitoring(self, obj):
        return TemplateItemSerializer(instance=self.get_task_template(obj, 'partial')['template_items'], many=True,
                                      fields=('id', 'role', 'type', 'aux_attributes')).data

    def get_task_workers_monitoring(self, obj):
        task_workers_filtered = obj.task_workers.exclude(task_status=models.TaskWorker.STATUS_SKIPPED)
        task_workers = TaskWorkerSerializer(instance=task_workers_filtered, many=True,
                                            fields=('id', 'task_status', 'worker_alias',
                                                    'task_worker_results_monitoring', 'updated_delta')).data
        return task_workers

    def get_has_comments(self, obj):
        return obj.taskcomment_task.count() > 0

    def get_project_data(self, obj):
        from crowdsourcing.serializers.project import ProjectSerializer
        project = ProjectSerializer(instance=obj.project, many=False, fields=('id', 'name', 'description', 'owner')).data
        return project


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ('name', 'iso_code', 'last_updated')
        read_only_fields = ('last_updated',)
