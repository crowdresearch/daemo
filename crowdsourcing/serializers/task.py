from __future__ import division

import ast
from operator import itemgetter

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from crowdsourcing import models
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.serializers.message import CommentSerializer
from crowdsourcing.serializers.template import TemplateSerializer
from crowdsourcing.tasks import create_tasks
from crowdsourcing.utils import get_template_string, hash_task
from crowdsourcing.validators.task import ItemValidator


class ReturnFeedbackSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.ReturnFeedback
        fields = ('id', 'body', 'task_worker', 'deleted_at', 'created_at', 'updated_at')

    def create(self, **kwargs):
        rf = models.ReturnFeedback(body=self.validated_data['body'],
                                   task_worker=self.validated_data['task_worker'])
        self.validated_data['task_worker'].returned_at = timezone.now()
        self.validated_data['task_worker'].save()
        rf.save()
        return rf


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
    key = serializers.SerializerMethodField()
    assignment_id = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskWorkerResult
        validators = [ItemValidator()]
        list_serializer_class = TaskWorkerResultListSerializer
        fields = ('id', 'template_item', 'result', 'key', 'created_at', 'updated_at', 'attachment', 'assignment_id')
        read_only_fields = ('created_at', 'updated_at', 'key', 'assignment_id')

    def create(self, **kwargs):
        return models.TaskWorkerResult.objects.get_or_create(kwargs.get('validated_data', self.validated_data))

    def get_key(self, obj):
        if obj is not None and obj.template_item is not None:
            return obj.template_item.name
        return None

    def get_assignment_id(self, obj):
        return obj.task_worker_id


class TaskWorkerSerializer(DynamicFieldsModelSerializer):
    import multiprocessing

    lock = multiprocessing.Lock()
    results = TaskWorkerResultSerializer(many=True, read_only=True,
                                         fields=('result', 'template_item', 'id', 'key'))
    worker_alias = serializers.SerializerMethodField()
    worker_rating = serializers.SerializerMethodField()
    updated_delta = serializers.SerializerMethodField()
    requester_alias = serializers.SerializerMethodField()
    project_data = serializers.SerializerMethodField()
    project_template = serializers.SerializerMethodField()
    # has_comments = serializers.SerializerMethodField()
    return_feedback = serializers.SerializerMethodField()
    task_data = serializers.SerializerMethodField()
    task_template = serializers.SerializerMethodField()
    expected = serializers.SerializerMethodField()
    task_group_id = serializers.SerializerMethodField()

    class Meta:
        model = models.TaskWorker
        fields = ('id', 'task', 'worker', 'status', 'created_at', 'updated_at',
                  'worker_alias', 'worker_rating', 'results',
                  'updated_delta', 'requester_alias', 'project_data', 'is_paid',
                  'return_feedback', 'task_data', 'expected', 'task_group_id', 'task_template', 'submitted_at',
                  'approved_at', 'project_template', 'attempt')
        read_only_fields = ('task', 'worker', 'results', 'created_at', 'updated_at',
                            'return_feedback', 'task_data', 'expected', 'task_group_id', 'submitted_at',
                            'approved_at', 'project_template', 'attempt')

    def create(self, **kwargs):
        project = kwargs['project']
        skipped = False
        task_worker = models.TaskWorker.objects.filter(worker=kwargs['worker'],
                                                       task__project__group_id=kwargs.get('group_id', project),
                                                       status=models.TaskWorker.STATUS_RETURNED) \
            .order_by('id').first()
        if task_worker is not None:
            session_count = models.TaskWorkerSession.objects.filter(ended_at__isnull=True).count()
            if session_count == 0:
                models.TaskWorkerSession.objects.create(task_worker=task_worker, started_at=timezone.now())
            return task_worker, 200

        task_worker = models.TaskWorker.objects.filter(~Q(id=kwargs.get('id')),
                                                       worker=kwargs['worker'], task__project_id=project,
                                                       status=models.TaskWorker.STATUS_IN_PROGRESS) \
            .order_by('id').first()
        if task_worker is not None:
            return task_worker, 200
        with self.lock:
            with transaction.atomic():  # select_for_update(nowait=False)
                # noinspection SqlResolve
                query = '''
                    SELECT
                      t.id,
                      p.id

                    FROM crowdsourcing_task t INNER JOIN (SELECT
                                                            group_id,
                                                            max(id) id
                                                          FROM crowdsourcing_task
                                                          WHERE deleted_at IS NULL
                                                          GROUP BY group_id) t_max ON t_max.id = t.id
                      INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                      INNER JOIN (
                                   SELECT
                                     t.group_id,
                                     sum(t.own)    own,
                                     sum(t.others) others
                                   FROM (
                                          SELECT
                                            t.group_id,
                                            CASE WHEN tw.worker_id = (%(worker_id)s)
                                              THEN 1
                                            ELSE 0 END own,
                                            CASE WHEN (tw.worker_id IS NOT NULL AND tw.worker_id <> (%(worker_id)s))
                                             AND tw.status NOT IN (4, 6, 7)
                                              THEN 1
                                            ELSE 0 END others
                                          FROM crowdsourcing_task t
                                            LEFT OUTER JOIN crowdsourcing_taskworker tw ON (t.id =
                                                                                            tw.task_id)
                                          WHERE exclude_at IS NULL AND t.deleted_at IS NULL) t
                                   GROUP BY t.group_id) t_count ON t_count.group_id = t.group_id
                    WHERE t_count.own = 0 AND t_count.others < p.repetition AND p.id=(%(project_id)s)
                    AND p.status = 3 and t.id <> %(task_id)s LIMIT 1
                    '''

                tasks = models.Task.objects.raw(query, params={'project_id': project,
                                                               'task_id': kwargs.get('task_id', -1),
                                                               'worker_id': kwargs['worker'].id})

                if not len(list(tasks)):
                    # noinspection SqlResolve
                    tasks = models.Task.objects.raw(
                        '''
                            SELECT
                                t.id,
                                t.group_id,
                                p.id project_id
                            FROM crowdsourcing_task t INNER JOIN (SELECT
                                                                    group_id,
                                                                    max(id) id
                                                                  FROM crowdsourcing_task
                                                                  WHERE deleted_at IS NULL
                                                                  GROUP BY group_id) t_max ON t_max.id = t.id
                              INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                              INNER JOIN (
                                           SELECT
                                             t.group_id,
                                             sum(t.own)    own,
                                             sum(t.others) others
                                           FROM (
                                                  SELECT
                                                    t.group_id,
                                                    CASE WHEN tw.worker_id = (%(worker_id)s)
                                                        AND (tw.status <> 6 OR tw.is_qualified is FALSE )
                                                      THEN 1
                                                    ELSE 0 END own,
                                                    CASE WHEN (tw.worker_id IS NOT NULL
                                                    AND tw.worker_id <> (%(worker_id)s))
                                                     AND tw.status NOT IN (4, 6, 7)
                                                      THEN 1
                                                    ELSE 0 END others
                                                  FROM crowdsourcing_task t
                                                    LEFT OUTER JOIN crowdsourcing_taskworker tw ON (t.id =
                                                                                                    tw.task_id)
                                                  WHERE exclude_at IS NULL AND t.deleted_at IS NULL) t
                                           GROUP BY t.group_id) t_count ON t_count.group_id = t.group_id
                            WHERE t_count.own = 0 AND t_count.others < p.repetition AND p.id=(%(project_id)s)
                            AND p.status = 3 and t.id <> %(task_id)s LIMIT 1
                        ''', params={'project_id': project, 'task_id': kwargs.get('task_id', -1),
                                     'worker_id': kwargs['worker'].id})
                    skipped = True
                if len(list(tasks)) and not skipped:
                    task_worker = models.TaskWorker.objects.create(worker=kwargs['worker'], task=tasks[0])
                    is_qualified = self.check_task_qualification(task_worker)
                    task_worker.is_qualified = is_qualified
                    if not is_qualified:
                        # task_worker.is_qualified = False
                        task_worker.status = models.TaskWorker.STATUS_SKIPPED
                        task_worker.save()
                elif len(list(tasks)) and skipped:
                    task_worker = models.TaskWorker.objects.get(worker=kwargs['worker'],
                                                                task__group_id=tasks[0].group_id)
                    task_worker.status = models.TaskWorker.STATUS_IN_PROGRESS
                    task_worker.started_at = timezone.now()
                    task_worker.task_id = tasks[0].id
                    task_worker.save()
        if task_worker is None:
            return {}, 204
        models.TaskWorkerSession.objects.create(task_worker=task_worker, started_at=timezone.now())
        return task_worker, 200

    @staticmethod
    def get_project_template(obj):
        return TemplateSerializer(instance=obj.task.project.template).data

    @staticmethod
    def check_task_qualification(instance):
        qualification = instance.task.project.qualification
        if qualification is not None:
            item = qualification.items.all().filter(scope='task').first()
            if item is not None and item.expression.get('attribute') == 'task_worker_id':
                try:
                    filter_data = instance.task.data.get(item.expression.get('value'))
                    if filter_data is not None:
                        task_worker_ids = ast.literal_eval(filter_data)
                        tasks = models.TaskWorker.objects.filter(
                            status__in=[models.TaskWorker.STATUS_SUBMITTED,
                                        models.TaskWorker.STATUS_ACCEPTED,
                                        models.TaskWorker.STATUS_RETURNED,
                                        models.TaskWorker.STATUS_REJECTED],
                            worker=instance.worker,
                            task__project__owner=instance.task.project.owner,
                            pk__in=task_worker_ids
                        )
                        if item.expression.get('operator') == 'in' and len(tasks) == 0:
                            return False
                        elif item.expression.get('operator') == 'not_in' and len(tasks) > 0:
                            return False
                except ValueError as e:
                    print(e)
        return True

    @staticmethod
    def get_worker_alias(obj):
        return obj.worker.profile.handle

    @staticmethod
    def get_worker_rating(obj):
        rating = models.Rating.objects.values('id', 'weight') \
            .filter(origin_id=obj.task.project.owner_id, target_id=obj.worker_id, task_id=obj.task_id,
                    origin_type=models.Rating.RATING_REQUESTER).order_by('-updated_at').first()
        if rating is None:
            rating = models.Rating.objects.values('id', 'weight') \
                .filter(origin_id=obj.task.project.owner_id, target_id=obj.worker_id).order_by('-updated_at').first()
        if rating is None:
            rating = {
                'id': None,
                'origin_type': models.Rating.RATING_REQUESTER,
                'weight': 2.0
            }
        rating.update({'target': obj.worker_id})
        return rating

    @staticmethod
    def get_updated_delta(obj):
        from crowdsourcing.utils import get_time_delta

        return get_time_delta(obj.updated_at)

    @staticmethod
    def get_requester_alias(obj):
        return obj.task.project.owner.profile.handle

    @staticmethod
    def get_project_data(obj):
        return {'id': obj.task.project.id, 'name': obj.task.project.name, 'price': obj.task.project.price,
                'discussion_link': obj.task.project.discussion_link}

    @staticmethod
    def get_has_comments(obj):
        return obj.task.comments.count() > 0

    @staticmethod
    def get_return_feedback(obj):
        return ReturnFeedbackSerializer(obj.return_feedback.first()).data

    @staticmethod
    def get_task_data(obj):
        return obj.task.data

    @staticmethod
    def get_task_group_id(obj):
        return obj.task.group_id

    @staticmethod
    def get_expected(obj):
        return max(models.TaskWorker.objects.filter(task_id=obj.task_id,
                                                    status__in=[models.TaskWorker.STATUS_ACCEPTED,
                                                                models.TaskWorker.STATUS_SUBMITTED]).count(),
                   obj.task.project.repetition)

    @staticmethod
    def get_task_template(obj):
        serializer = TaskSerializer(instance=obj.task,
                                    fields=('id', 'template'),
                                    context={'task_worker': obj})
        return serializer.data


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


class BatchSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Batch


class TaskSerializer(DynamicFieldsModelSerializer):
    task_workers = TaskWorkerSerializer(many=True, read_only=True)
    template = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()
    project_data = serializers.SerializerMethodField()
    comments = TaskCommentSerializer(many=True, read_only=True)
    updated_at = serializers.SerializerMethodField()
    worker_count = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    data = serializers.JSONField()
    batch = BatchSerializer(required=False)

    class Meta:
        model = models.Task
        fields = ('id', 'project', 'deleted_at', 'created_at', 'updated_at', 'data',
                  'task_workers', 'template', 'project_data',
                  'has_comments', 'comments', 'worker_count',
                  'completed', 'total', 'row_number', 'rerun_key', 'batch', 'price', 'hash', 'group_id')
        read_only_fields = ('created_at', 'updated_at', 'deleted_at', 'has_comments', 'comments', 'project_data',
                            'row_number', 'batch', 'price', 'hash', 'group_id')

    def create(self, **kwargs):
        data = self.validated_data.pop('data', {})
        hash_digest = hash_task(data)
        task = models.Task.objects.create(data=data, hash=hash_digest, **self.validated_data)
        task.group_id = task.id
        task.save()
        return task

    @staticmethod
    def bulk_create(data, *args, **kwargs):
        return models.Task.objects.bulk_create(data)

    @staticmethod
    def create_initial(tasks):
        create_tasks.delay(tasks)

    @staticmethod
    def delete(instance):
        instance.delete()
        return instance

    @staticmethod
    def bulk_update(instances, data):
        instances.update(**data)
        return instances

    def get_template(self, obj, return_type='full'):
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
            if 'src' in aux_attrib:
                aux_attrib['src'] = get_template_string(aux_attrib['src'], data)[0]

            if 'question' in aux_attrib:
                return_value, has_variables = get_template_string(aux_attrib['question']['value'], data)
                aux_attrib['question']['value'] = return_value
                aux_attrib['question']['is_static'] = not has_variables

            if 'options' in aux_attrib:

                if obj.project.is_review and 'task_workers' in obj.data:
                    aux_attrib['options'] = []
                    display_labels = ['Top one', 'Bottom one']
                    sorted_task_workers = sorted(obj.data['task_workers'], key=itemgetter('task_worker'))
                    # TODO change this to id
                    for index, tw in enumerate(sorted_task_workers):
                        aux_attrib['options'].append(
                            {
                                "value": tw['task_worker'],
                                "display_value": display_labels[index],
                                "data_source": [],
                                "position": index + 1
                            }
                        )
                for option in aux_attrib['options']:
                    option['value'] = get_template_string(option['value'], data)[0]

            if item['type'] == 'iframe':
                from django.conf import settings
                from hashids import Hashids
                identifier = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
                if hasattr(task_worker, 'id'):
                    item['identifier'] = identifier.encode(task_worker.id, task_worker.task.id, item['id'])
                else:
                    item['identifier'] = 'READ_ONLY'
                item['daemo_post_url'] = settings.SITE_HOST + '/api/done/'
            if item['role'] == 'input' and task_worker is not None:
                for result in task_worker.results.all():
                    if item['type'] == 'checkbox' and result.template_item_id == item['id']:
                        item['aux_attributes']['options'] = result.result  # might need to loop through options
                    elif item['type'] == 'file_upload' and result.template_item_id == item['id']:
                        item['answer'] = {
                            "name": result.attachment.name,
                            "url": result.attachment.file.url
                        }
                    elif result.template_item_id == item['id']:
                        item['answer'] = result.result

        # template['items'] = sorted(template['items'], key=lambda k: k['position'])
        return template

    @staticmethod
    def get_has_comments(obj):
        return obj.comments.count() > 0

    @staticmethod
    def get_project_data(obj):
        from crowdsourcing.serializers.project import ProjectSerializer
        project = ProjectSerializer(instance=obj.project, many=False,
                                    fields=('id', 'name', 'hash_id',
                                            'repetition', 'price', 'discussion_link', 'is_prototype')).data
        return project

    @staticmethod
    def get_updated_at(obj):
        from crowdsourcing.utils import get_time_delta
        return get_time_delta(obj.updated_at)

    @staticmethod
    def get_worker_count(obj):
        return obj.task_workers.filter(status__in=[2, 3, 5]).count()

    @staticmethod
    def get_completed(obj):
        return obj.task_workers.filter(status__in=[2, 3, 5]).count()

    @staticmethod
    def get_total(obj):
        return obj.project.repetition


class CollectiveRejectionSerializer(DynamicFieldsModelSerializer):
    detail = serializers.CharField(required=False)

    class Meta:
        model = models.CollectiveRejection
        fields = ('id', 'detail', 'reason')

    def create(self, **kwargs):
        reason = self.validated_data.get('reason')
        detail = self.validated_data.get('detail', None)
        if reason == models.CollectiveRejection.REASON_OTHER and not detail:
            raise ValidationError("Detail is required when Other is selected")
        return models.CollectiveRejection.objects.create(reason=reason, detail=detail)
