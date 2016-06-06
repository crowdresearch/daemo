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
        validators = [ItemValidator()]
        list_serializer_class = TaskWorkerResultListSerializer
        fields = ('id', 'template_item', 'result', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def create(self, **kwargs):
        models.TaskWorkerResult.objects.get_or_create(self.validated_data)


class TaskWorkerSerializer(DynamicFieldsModelSerializer):
    import multiprocessing

    lock = multiprocessing.Lock()
    results = TaskWorkerResultSerializer(many=True, read_only=True,
                                         fields=('result', 'template_item', 'id'))
    worker_alias = serializers.SerializerMethodField()
    worker_rating = serializers.SerializerMethodField()
    updated_delta = serializers.SerializerMethodField()
    requester_alias = serializers.SerializerMethodField()
    project_data = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskWorker
        fields = ('id', 'task', 'worker', 'status', 'created_at', 'updated_at',
                  'worker_alias', 'worker_rating', 'results',
                  'updated_delta',
                  'requester_alias', 'project_data', 'is_paid', 'has_comments')
        read_only_fields = ('task', 'worker', 'results', 'created_at', 'updated_at',
                            'has_comments')

    def create(self, **kwargs):
        project = kwargs['project']
        skipped = False
        task_worker = {}
        with self.lock:
            with transaction.atomic():  # select_for_update(nowait=False)
                query = '''
                    SELECT
                      t.id,
                      t.project_id,
                      tw.status,
                      t.data,
                      t.deleted_at,
                      t.created_at,
                      t.updated_at,
                      p.price
                    FROM crowdsourcing_task t
                      INNER JOIN crowdsourcing_project p
                        ON (t.project_id = p.id)
                      LEFT OUTER JOIN crowdsourcing_taskworker tw ON (
                        t.id = tw.task_id
                        AND tw.status NOT IN (4, 6, 7)
                        )
                    WHERE (t.project_id = %s)
                    GROUP BY t.id, t.project_id,
                      tw.status, t.data,
                      t.deleted_at,
                      t.created_at,
                      t.updated_at, p.price,
                      p.repetition, tw.task_id
                    HAVING p.repetition > (COUNT(tw.id))
                           AND t.id NOT IN (SELECT tw1.task_id
                                                FROM crowdsourcing_taskworker tw1
                                                WHERE tw1.worker_id =%s)
                    LIMIT 1
                    '''

                tasks = models.Task.objects.raw(query, params=[project, kwargs['worker'].id])

                if not len(list(tasks)):
                    tasks = models.Task.objects.raw(
                        '''
                        SELECT
                          t.id,
                          t.project_id,
                          tw.status,
                          t.data,
                          t.deleted_at,
                          t.created_at,
                          t.updated_at,
                          p.price
                        FROM crowdsourcing_task t
                          INNER JOIN crowdsourcing_project p
                            ON (t.project_id = p.id)
                          LEFT OUTER JOIN crowdsourcing_taskworker tw
                            ON (t.id = tw.task_id
                                AND tw.status NOT IN (4, 6, 7))
                        WHERE (t.project_id = %s)
                        GROUP BY t.id, t.project_id,
                          tw.status,
                          t.data, t.deleted_at,
                          t.created_at,
                          t.updated_at, p.price,
                          p.repetition, tw.task_id
                        HAVING p.repetition > (COUNT(tw.id))
                               AND t.id IN (SELECT tw1.task_id
                                                             FROM
                                                               crowdsourcing_taskworker tw1
                                                             WHERE worker_id =%s AND status = 6)
                        ORDER BY random()
                        ''', params=[project, kwargs['worker'].id])
                    skipped = True
                if len(list(tasks)) and not skipped:
                    task_worker = models.TaskWorker.objects.create(worker=kwargs['worker'], task=tasks[0])

                elif len(list(tasks)) and skipped:
                    task_worker = models.TaskWorker.objects.get(worker=kwargs['worker'], task=tasks[0])
                    task_worker.status = 1
                    task_worker.save()
                else:
                    return {}, 204
                return task_worker, 200

    @staticmethod
    def get_worker_alias(obj):
        return obj.worker.username

    @staticmethod
    def get_worker_rating(obj):
        rating = models.Rating.objects.values('id', 'weight') \
            .filter(origin_id=obj.task.project.owner_id, target_id=obj.worker_id) \
            .order_by('-updated_at').first()
        if rating is None:
            rating = {
                'id': None,
                'origin_type': 2
            }
        rating.update({'target': obj.worker_id})
        return rating

    @staticmethod
    def get_updated_delta(obj):
        from crowdsourcing.utils import get_time_delta

        return get_time_delta(obj.updated_at)

    @staticmethod
    def get_requester_alias(obj):
        return obj.task.project.owner.username

    @staticmethod
    def get_project_data(obj):
        return {'id': obj.task.project.id, 'name': obj.task.project.name, 'price': obj.task.project.price}

    @staticmethod
    def get_has_comments(obj):
        return obj.task.comments.count() > 0


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
    # project_data = serializers.SerializerMethodField()
    comments = TaskCommentSerializer(many=True, read_only=True)
    updated_at = serializers.SerializerMethodField()
    worker_count = serializers.SerializerMethodField()
    completion = serializers.SerializerMethodField()
    data = serializers.JSONField()

    class Meta:
        model = models.Task
        fields = ('id', 'project', 'deleted_at', 'created_at', 'updated_at', 'data',
                  'task_workers', 'template',
                  'has_comments', 'comments', 'worker_count',
                  'completion')
        read_only_fields = ('created_at', 'updated_at', 'deleted_at', 'has_comments', 'comments', 'project_data')

    def create(self, **kwargs):
        task = models.Task.objects.create(**self.validated_data)
        return task

    def bulk_create(self, data, *args, **kwargs):
        return models.Task.objects.bulk_create(data)

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
            template = TemplateSerializer(instance=obj.project.template, many=False).data
        else:
            template = \
                TemplateSerializer(instance=obj.project.template, many=False, fields=('id', 'items')).data
        data = obj.data
        if 'task_worker' in self.context:
            task_worker = self.context['task_worker']
        for item in template['items']:
            aux_attrib = item['aux_attributes']
            if 'data_source' in aux_attrib and aux_attrib['data_source'] is not None and \
                    'src' in aux_attrib:
                for data_source in aux_attrib['data_source']:
                    if 'value' in data_source and data_source['value'] is not None:
                        parsed_data_source_value = ' '.join(data_source['value'].split())
                        if parsed_data_source_value in data:
                            aux_attrib['src'] = aux_attrib['src'] \
                                .replace('{' + str(data_source['value']) + '}', str(data[parsed_data_source_value]))
            if 'question' in aux_attrib and 'data_source' in aux_attrib['question'] and \
                    aux_attrib['question']['data_source'] is not None:
                for data_source in aux_attrib['question']['data_source']:
                    if 'value' in data_source and data_source['value'] is not None:
                        parsed_data_source_value = ' '.join(data_source['value'].split())
                        if parsed_data_source_value in data:
                            aux_attrib['question']['value'] = aux_attrib['question']['value'] \
                                .replace('{' + str(data_source['value']) + '}', str(data[parsed_data_source_value]))
            if 'options' in aux_attrib:
                for option in aux_attrib['options']:
                    if 'data_source' in option and option['data_source'] is not None:
                        for data_source in option['data_source']:
                            if 'value' in data_source and data_source['value'] is not None:
                                parsed_data_source_value = ' '.join(data_source['value'].split())
                                if parsed_data_source_value in data:
                                    option['value'] = option['value'] \
                                        .replace('{' + str(data_source['value']) + '}',
                                                 str(data[parsed_data_source_value]))
            if item['type'] == 'iframe':
                from django.conf import settings
                from hashids import Hashids
                identifier = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
                if hasattr(task_worker, 'id'):
                    item['identifier'] = identifier.encode(task_worker.id, task_worker.task.id, item['id'])
                else:
                    item['identifier'] = 'READ_ONLY'
            if item['role'] == 'input' and task_worker is not None:
                for result in task_worker.results.all():
                    if item['type'] == 'checkbox' and result.template_item_id == item['id']:
                        item['aux_attributes']['options'] = result.result  # might need to loop through options
                    elif result.template_item_id == item['id']:
                        item['answer'] = result.result
            if 'pattern' in aux_attrib:
                del aux_attrib['pattern']

        template['items'] = sorted(template['items'], key=lambda k: k['position'])
        return template

    @staticmethod
    def get_has_comments(obj):
        return obj.comments.count() > 0

    @staticmethod
    def get_project_data(obj):
        from crowdsourcing.serializers.project import ProjectSerializer
        project = ProjectSerializer(instance=obj.project, many=False, fields=('id', 'name', 'owner')).data
        return project

    @staticmethod
    def get_updated_at(obj):
        from crowdsourcing.utils import get_time_delta
        return get_time_delta(obj.updated_at)

    @staticmethod
    def get_worker_count(obj):
        return obj.task_workers.filter(status__in=[2, 3, 5]).count()

    @staticmethod
    def get_completion(obj):
        return str(obj.task_workers.filter(status__in=[2, 3, 5]).count()) + '/' + str(obj.project.repetition)
