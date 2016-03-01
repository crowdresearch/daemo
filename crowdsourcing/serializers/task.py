from __future__ import division

from rest_framework import serializers
from django.db import transaction

from crowdsourcing import models
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.serializers.template import TemplateSerializer
from crowdsourcing.serializers.message import CommentSerializer
from crowdsourcing.validators.task import ItemValidator


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
    result = serializers.JSONField(allow_null=True)

    class Meta:
        model = models.TaskWorkerResult
        validators = [
            ItemValidator()
        ]
        list_serializer_class = TaskWorkerResultListSerializer
        fields = ('id', 'template_item', 'result', 'status', 'created_timestamp', 'last_updated')
        read_only_fields = ('created_timestamp', 'last_updated')

    def create(self, **kwargs):
        models.TaskWorkerResult.objects.get_or_create(self.validated_data)


class TaskWorkerSerializer(DynamicFieldsModelSerializer):
    import multiprocessing

    lock = multiprocessing.Lock()
    task_worker_results = TaskWorkerResultSerializer(many=True, read_only=True,
                                                     fields=('result', 'template_item', 'id'))
    worker_alias = serializers.SerializerMethodField()
    worker_rating = serializers.SerializerMethodField()
    updated_delta = serializers.SerializerMethodField()
    requester_alias = serializers.SerializerMethodField()
    project_data = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskWorker
        fields = ('id', 'task', 'worker', 'task_status', 'created_timestamp', 'last_updated',
                  'worker_alias', 'worker_rating', 'task_worker_results',
                  'updated_delta',
                  'requester_alias', 'project_data', 'is_paid', 'has_comments')
        read_only_fields = ('task', 'worker', 'task_worker_results', 'created_timestamp', 'last_updated',
                            'has_comments')

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
                      AND crowdsourcing_taskworker.task_status NOT IN (4,6)
                      )
                    WHERE ("crowdsourcing_task"."project_id" = %s)
                    GROUP BY "crowdsourcing_task"."id", "crowdsourcing_task"."project_id",
                        "crowdsourcing_task"."status", "crowdsourcing_task"."data",
                        "crowdsourcing_task"."deleted",
                       "crowdsourcing_task"."created_timestamp",
                      "crowdsourcing_task"."last_updated", "crowdsourcing_task"."price",
                      "crowdsourcing_project"."repetition", crowdsourcing_taskworker.task_id
                    HAVING "crowdsourcing_project"."repetition" > (COUNT("crowdsourcing_taskworker"."id"))
                    AND "crowdsourcing_task"."id" NOT IN (SELECT "crowdsourcing_taskworker"."task_id"
                    FROM "crowdsourcing_taskworker"
                    WHERE "crowdsourcing_taskworker"."worker_id"=%s) LIMIT 1'''

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
                          AND crowdsourcing_taskworker.task_status NOT IN (4,6))
                        WHERE ("crowdsourcing_task"."project_id" = %s)
                        GROUP BY "crowdsourcing_task"."id", "crowdsourcing_task"."project_id",
                          "crowdsourcing_task"."status",
                          "crowdsourcing_task"."data", "crowdsourcing_task"."deleted",
                          "crowdsourcing_task"."created_timestamp",
                          "crowdsourcing_task"."last_updated", "crowdsourcing_task"."price",
                          "crowdsourcing_project"."repetition", crowdsourcing_taskworker.task_id
                        HAVING "crowdsourcing_project"."repetition" > (COUNT("crowdsourcing_taskworker"."id"))
                        AND crowdsourcing_task.id IN (SELECT crowdsourcing_taskworker.task_id FROM
                        crowdsourcing_taskworker WHERE worker_id=%s AND task_status=6) ORDER BY random()
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

    @staticmethod
    def get_worker_alias(obj):
        return obj.worker.alias

    @staticmethod
    def get_worker_rating(obj):
        rating = models.WorkerRequesterRating.objects.values('id', 'weight') \
            .filter(origin_id=obj.task.project.owner.profile_id, target_id=obj.worker.profile_id) \
            .order_by('-last_updated').first()
        if rating is None:
            rating = {
                'id': None,
                'origin_type': 'requester'
            }
        rating.update({'target': obj.worker.profile_id})
        return rating

    @staticmethod
    def get_updated_delta(obj):
        from crowdsourcing.utils import get_time_delta

        return get_time_delta(obj.last_updated)

    @staticmethod
    def get_requester_alias(obj):
        return obj.task.project.owner.alias

    @staticmethod
    def get_project_data(obj):
        return {'id': obj.task.project.id, 'name': obj.task.project.name, 'price': obj.task.project.price}

    @staticmethod
    def get_has_comments(obj):
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
    template = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()
    project_data = serializers.SerializerMethodField()
    comments = TaskCommentSerializer(many=True, source='taskcomment_task', read_only=True)
    last_updated = serializers.SerializerMethodField()
    worker_count = serializers.SerializerMethodField()
    completion = serializers.SerializerMethodField()
    data = serializers.JSONField()

    class Meta:
        model = models.Task
        fields = ('id', 'project', 'status', 'deleted', 'created_timestamp', 'last_updated', 'data',
                  'task_workers', 'template',
                  'has_comments', 'comments', 'project_data', 'worker_count',
                  'completion')
        read_only_fields = ('created_timestamp', 'last_updated', 'deleted', 'has_comments', 'comments', 'project_data')

    def create(self, **kwargs):
        task = models.Task.objects.create(**self.validated_data)
        return task

    def update(self, instance, validated_data):
        validated_data.pop('project')
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    @staticmethod
    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

    def get_template(self, obj, return_type='full'):
        template = None
        task_worker = None
        if return_type == 'full':
            template = TemplateSerializer(instance=obj.project.templates, many=True).data[0]
        else:
            template = \
                TemplateSerializer(instance=obj.project.templates, many=True, fields=('id', 'template_items')).data[0]
        data = obj.data
        if 'task_worker' in self.context:
            task_worker = self.context['task_worker']
        for item in template['template_items']:
            aux_attrib = item['aux_attributes']
            if 'data_source' in aux_attrib and aux_attrib['data_source'] is not None and \
                    aux_attrib['data_source'] in data and 'src' in aux_attrib:
                aux_attrib['src'] = data[aux_attrib['data_source']]
            if 'question' in aux_attrib and 'data_source' in aux_attrib['question'] and \
                    aux_attrib['question']['data_source'] is not None and \
                    aux_attrib['question']['data_source'] in data.keys():
                aux_attrib['question']['value'] = data[aux_attrib['question']['data_source']]
            if 'options' in aux_attrib:
                for option in aux_attrib['options']:
                    if 'data_source' in option and option['data_source'] is not None and \
                            option['data_source'] in data.keys():
                        option['value'] = data[option['data_source']]
            if item['type'] == 'iframe':
                from django.conf import settings
                from hashids import Hashids
                identifier = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
                if hasattr(task_worker, 'id'):
                    item['identifier'] = identifier.encode(task_worker.id, task_worker.task.id, item['id'])
                else:
                    item['identifier'] = 'READ_ONLY'
            if item['role'] == 'input' and task_worker is not None:
                for result in task_worker.task_worker_results.all():
                    if item['type'] == 'checkbox' and result.template_item_id == item['id']:
                        item['aux_attributes']['options'] = result.result  # might need to loop through options
                    elif result.template_item_id == item['id']:
                        item['answer'] = result.result

        template['template_items'] = sorted(template['template_items'], key=lambda k: k['position'])
        return template

    @staticmethod
    def get_has_comments(obj):
        return obj.taskcomment_task.count() > 0

    @staticmethod
    def get_project_data(obj):
        from crowdsourcing.serializers.project import ProjectSerializer
        project = ProjectSerializer(instance=obj.project, many=False, fields=('id', 'name', 'owner')).data
        return project

    @staticmethod
    def get_last_updated(obj):
        from crowdsourcing.utils import get_time_delta
        return get_time_delta(obj.last_updated)

    @staticmethod
    def get_worker_count(obj):
        return obj.task_workers.filter(task_status__in=[2, 3, 5]).count()

    @staticmethod
    def get_completion(obj):
        return str(obj.task_workers.filter(task_status__in=[2, 3, 5]).count()) + '/' + str(obj.project.repetition)
