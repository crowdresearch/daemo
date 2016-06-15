import copy

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from crowdsourcing import models
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.serializers.message import CommentSerializer
from crowdsourcing.serializers.task import TaskSerializer, TaskCommentSerializer
from crowdsourcing.serializers.template import TemplateSerializer
from crowdsourcing.serializers.user import UserSerializer
from crowdsourcing.utils import generate_random_id
from crowdsourcing.serializers.file import BatchFileSerializer
from crowdsourcing.serializers.payment import TransactionSerializer
from crowdsourcing.validators.project import ProjectValidator
from mturk.tasks import mturk_update_status


class ProjectSerializer(DynamicFieldsModelSerializer):
    total_tasks = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()
    available_tasks = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    requester_rating = serializers.FloatField(read_only=True, required=False)
    raw_rating = serializers.IntegerField(read_only=True, required=False)

    owner = UserSerializer(fields=('username', 'id'), read_only=True)
    batch_files = BatchFileSerializer(many=True, read_only=True,
                                      fields=('id', 'name', 'size', 'column_headers', 'format', 'number_of_rows'))
    template = TemplateSerializer(many=False, required=False)

    name = serializers.CharField(default='Untitled Project')
    status = serializers.IntegerField(default=models.Project.STATUS_DRAFT)
    file_id = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    num_rows = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    deadline = serializers.DateTimeField(required=False)

    class Meta:
        model = models.Project
        fields = ('id', 'name', 'owner', 'description', 'status', 'repetition', 'deadline', 'timeout', 'template',
                  'batch_files', 'deleted_at', 'created_at', 'updated_at', 'price', 'has_data_set',
                  'data_set_location', 'total_tasks', 'file_id', 'age', 'is_micro', 'is_prototype', 'task_time',
                  'allow_feedback', 'feedback_permissions', 'min_rating', 'has_comments',
                  'available_tasks', 'comments', 'num_rows', 'requester_rating', 'raw_rating', 'post_mturk',
                  'qualification')
        read_only_fields = (
            'created_at', 'updated_at', 'deleted_at', 'owner', 'has_comments', 'available_tasks',
            'comments', 'template')

        validators = [ProjectValidator()]

    def create(self, with_defaults=True, **kwargs):
        template_initial = self.validated_data.pop('template') if 'template' in self.validated_data else None
        template_items = template_initial['items'] if template_initial else []

        template = {
            "name": 't_' + generate_random_id(),
            "items": template_items
        }

        template_serializer = TemplateSerializer(data=template)

        project = models.Project.objects.create(owner=kwargs['owner'], **self.validated_data)
        if template_serializer.is_valid():
            template = template_serializer.create(with_defaults=with_defaults, owner=kwargs['owner'])
            project.template = template
        else:
            raise ValidationError(template_serializer.errors)

        # models.ProjectTemplate.objects.get_or_create(project=project, template=template)

        if not with_defaults:
            project.status = models.Project.STATUS_IN_PROGRESS
            project.published_at = timezone.now()
            self.create_task(project.id)
            self.instance = project
            if not project.is_paid:
                self.pay()
        project.save()
        return project

    @staticmethod
    def get_age(model):
        from crowdsourcing.utils import get_time_delta

        if model.status == models.Project.STATUS_DRAFT:
            return "Saved " + get_time_delta(model.updated_at)
        else:
            return "Posted " + get_time_delta(model.published_at)

    @staticmethod
    def get_total_tasks(obj):
        return obj.tasks.all().count()

    @staticmethod
    def get_has_comments(obj):
        return obj.comments.count() > 0

    def get_available_tasks(self, obj):
        available_task_count = models.Project.objects.values('id').raw('''
            SELECT count(*) id
            FROM (
                   SELECT t.id
                   FROM crowdsourcing_task t
                     INNER JOIN crowdsourcing_project p ON (t.project_id = p.id)
                     LEFT OUTER JOIN crowdsourcing_taskworker tw ON (t.id =
                                                                     tw.task_id AND
                                                                     tw.status NOT IN (4, 6, 7))
                   WHERE (t.project_id =%s AND NOT (
                     (t.id IN (SELECT U1.task_id AS Col1
                                   FROM crowdsourcing_taskworker U1
                                   WHERE U1.worker_id =%s AND U1.status <> 6))))
                   GROUP BY t.id, p.repetition
                   HAVING p.repetition > (COUNT(tw.id))) available_tasks
            ''', params=[obj.id, self.context['request'].user.id])[0].id
        return available_task_count

    @staticmethod
    def get_comments(obj):
        if obj:
            comments = []
            tasks = obj.tasks.all()
            for task in tasks:
                task_comments = task.comments.all()
                for task_comment in task_comments:
                    comments.append(task_comment)
            serializer = TaskCommentSerializer(many=True, instance=comments, read_only=True)
            return serializer.data
        return []

    def has_csv_linkage(self, items):
        if items.count() > 0:
            template_items = items.all()
            for item in template_items:
                attribs = item.aux_attributes
                if 'question' in attribs \
                    and 'data_source' in attribs['question'] \
                        and attribs['question']['data_source'] is not None:
                    return True

                if 'options' in attribs and attribs['options'] is not None:
                    for option in attribs['options']:
                        if 'data_source' in option and option['data_source'] is not None:
                            return True
        return False

    def update(self, *args, **kwargs):
        status = self.validated_data.get('status', self.instance.status)
        # self.create_revision(None, *args, **kwargs)
        num_rows = self.validated_data.get('num_rows', 0)

        if self.instance.status != status and status == models.Project.STATUS_PUBLISHED:
            if self.instance.template.items.count() == 0:
                raise ValidationError('At least one template item is required')

            if self.instance.batch_files.count() == 0 or not self.has_csv_linkage(
                self.instance.template.items
            ):
                self.create_task(self.instance.id)
            else:
                batch_file = self.instance.batch_files.first()
                data = batch_file.parse_csv()
                count = 0

                for row in data:
                    if count == num_rows:
                        break
                    task = {
                        'project': self.instance.id,
                        'data': row
                    }
                    task_serializer = TaskSerializer(data=task)
                    if task_serializer.is_valid():
                        task_serializer.create(**kwargs)
                        count += 1
                    else:
                        raise ValidationError(task_serializer.errors)

            self.instance.published_at = timezone.now()
            status = models.Project.STATUS_IN_PROGRESS

        self.instance.name = self.validated_data.get('name', self.instance.name)
        self.instance.price = self.validated_data.get('price', self.instance.price)
        self.instance.repetition = self.validated_data.get('repetition', self.instance.repetition)
        self.instance.deadline = self.validated_data.get('deadline', self.instance.deadline)
        self.instance.timeout = self.validated_data.get('timeout', self.instance.timeout)
        self.instance.post_mturk = self.validated_data.get('post_mturk', self.instance.post_mturk)

        if status != self.instance.status \
            and status in (models.Project.STATUS_PAUSED, models.Project.STATUS_IN_PROGRESS) and \
                self.instance.status in (models.Project.STATUS_PAUSED, models.Project.STATUS_IN_PROGRESS):
            mturk_update_status.delay({'id': self.instance.id, 'status': status})

        self.instance.status = status
        self.instance.save()
        if status == models.Project.STATUS_IN_PROGRESS and not self.instance.is_paid:
            self.pay()

        return self.instance

    @staticmethod
    def create_task(project_id):
        task_data = {
            "project": project_id,
            "data": {}
        }

        task_serializer = TaskSerializer(data=task_data)

        if task_serializer.is_valid():
            task_serializer.create()
        else:
            raise ValidationError(task_serializer.errors)

    def fork(self, *args, **kwargs):
        template = self.instance.template
        template_items = copy.copy(template.items.all())
        categories = self.instance.categories.all()
        batch_files = self.instance.batch_files.all()

        project = self.instance
        project.name += ' (copy)'
        project.status = 1
        project.is_prototype = False
        project.parent = models.Project.objects.get(pk=self.instance.id)
        template.pk = None
        template.save()
        project.template = template

        for template_item in template_items:
            template_item.pk = None
            template_item.template = template
            template_item.save()
        project.id = None
        project.save()

        for category in categories:
            project_category = models.ProjectCategory(project=project, category=category)
            project_category.save()
        for batch_file in batch_files:
            project_batch_file = models.ProjectBatchFile(project=project, batch_file=batch_file)
            project_batch_file.save()

    def pay(self, *args, **kwargs):
        task_count = self.instance.project_tasks.count()
        transaction_data = {
            'sender': models.FinancialAccount.objects.get(owner_id=self.instance.owner.profile_id, type='requester',
                                                          is_system=False).id,
            'recipient': models.FinancialAccount.objects.get(is_system=True, type='escrow').id,
            'amount': self.instance.repetition * task_count * self.instance.price,
            'method': 'daemo',
            'sender_type': 'project_owner',
            'reference': 'P#' + str(self.instance.id)
        }

        transaction_serializer = TransactionSerializer(data=transaction_data)
        if transaction_serializer.is_valid():
            transaction_serializer.create()
            self.instance.is_paid = True
            self.instance.save()
        else:
            raise ValidationError('Error in payment')


class QualificationApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification


class QualificationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QualificationItem


class ProjectCommentSerializer(DynamicFieldsModelSerializer):
    comment = CommentSerializer()

    class Meta:
        model = models.ProjectComment
        fields = ('id', 'project', 'comment')
        read_only_fields = ('project',)

    def create(self, **kwargs):
        comment_data = self.validated_data.pop('comment')
        comment_serializer = CommentSerializer(data=comment_data)
        if comment_serializer.is_valid():
            comment = comment_serializer.create(sender=kwargs['sender'])
            project_comment = models.ProjectComment.objects.create(project_id=kwargs['project'], comment_id=comment.id)
            return {'id': project_comment.id, 'comment': comment}


class ProjectBatchFileSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.ProjectBatchFile
        fields = ('id', 'project', 'batch_file')
        read_only_fields = ('project',)

    def create(self, project=None, **kwargs):
        project_file = models.ProjectBatchFile.objects.create(project_id=project, **self.validated_data)
        return project_file


class CategorySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'parent')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.parent = validated_data.get('parent', instance.parent)
        instance.save()
        return instance
