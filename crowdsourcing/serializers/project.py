import copy

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from crowdsourcing.crypto import to_hash
from crowdsourcing import models
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.serializers.message import CommentSerializer
from crowdsourcing.serializers.task import TaskSerializer, TaskCommentSerializer
from crowdsourcing.serializers.template import TemplateSerializer
from crowdsourcing.serializers.user import UserSerializer
from crowdsourcing.utils import generate_random_id
from crowdsourcing.serializers.file import BatchFileSerializer
from crowdsourcing.serializers.payment import TransactionSerializer
from crowdsourcing.tasks import update_project_boomerang
from crowdsourcing.validators.project import ProjectValidator
from mturk.tasks import mturk_update_status


class ProjectSerializer(DynamicFieldsModelSerializer):
    total_tasks = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()
    available_tasks = serializers.IntegerField(read_only=True)
    in_progress = serializers.IntegerField(read_only=True)
    completed = serializers.IntegerField(read_only=True)
    awaiting_review = serializers.IntegerField(read_only=True)
    comments = serializers.SerializerMethodField()
    relaunch = serializers.SerializerMethodField()

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
    revisions = serializers.SerializerMethodField()
    hash_id = serializers.SerializerMethodField()
    review_price = serializers.FloatField(required=False)

    class Meta:
        model = models.Project
        fields = ('id', 'name', 'owner', 'description', 'status', 'repetition', 'deadline', 'timeout', 'template',
                  'batch_files', 'deleted_at', 'created_at', 'updated_at', 'price', 'has_data_set',
                  'data_set_location', 'total_tasks', 'file_id', 'age', 'is_micro', 'is_prototype', 'has_review',
                  'task_time', 'allow_feedback', 'feedback_permissions', 'min_rating', 'has_comments',
                  'available_tasks', 'comments', 'num_rows', 'requester_rating', 'raw_rating', 'post_mturk',
                  'qualification', 'relaunch', 'group_id', 'revisions', 'hash_id', 'is_api_only', 'in_progress',
                  'awaiting_review', 'completed', 'review_price')
        read_only_fields = (
            'created_at', 'updated_at', 'deleted_at', 'owner', 'has_comments', 'available_tasks',
            'comments', 'template', 'is_api_only')

        validators = [ProjectValidator()]

    def to_representation(self, instance):
        data = super(ProjectSerializer, self).to_representation(instance)
        task_time = int(instance.task_time.total_seconds() / 60) if instance.task_time is not None else None
        timeout = int(instance.timeout.total_seconds() / 60) if instance.timeout is not None else None
        review_project = instance.projects.all().filter(is_review=True).first()
        if review_project is not None:
            review_price = review_project.price
            data.update({'review_price': review_price})
        data.update({'task_time': task_time, 'timeout': timeout})
        data.update({'price': instance.price})
        return data

    def to_internal_value(self, data):
        if 'task_time' in data and data['task_time'] is not None:
            data['task_time'] = "00:{}:00".format(data['task_time'])
        if 'timeout' in data and data['timeout'] is not None:
            data['timeout'] = "00:{}:00".format(data['timeout'])
        return super(ProjectSerializer, self).to_internal_value(data)

    def create(self, with_defaults=True, **kwargs):
        template_initial = self.validated_data.pop('template') if 'template' in self.validated_data else None
        template_items = template_initial['items'] if template_initial else []

        template = {
            "name": 't_' + generate_random_id(),
            "items": template_items
        }

        template_serializer = TemplateSerializer(data=template)
        self.validated_data.pop('post_mturk')
        project = models.Project.objects.create(owner=kwargs['owner'], post_mturk=True, amount_due=0,
                                                **self.validated_data)
        if template_serializer.is_valid():
            project_template = template_serializer.create(with_defaults=with_defaults, is_review=False,
                                                          owner=kwargs['owner'])
            project.template = project_template
        else:
            raise ValidationError(template_serializer.errors)

        project.group_id = project.id

        project_name = 'Peer Review for ' + project.name

        review_project = models.Project.objects.create(name=project_name, owner=project.owner,
                                                       parent=project, is_prototype=False,
                                                       is_review=True)
        template_serializer = TemplateSerializer(data=template)
        if template_serializer.is_valid():
            review_template = template_serializer.create(with_defaults=False, is_review=True,
                                                         owner=project.owner)
            review_project.template = review_template
        else:
            raise ValidationError(template_serializer.errors)
        review_project.group_id = review_project.id
        review_project.save()

        if not with_defaults:
            project.status = models.Project.STATUS_IN_PROGRESS
            project.published_at = timezone.now()
            self.instance = project
            if not project.is_paid:
                self.pay(self.instance.price * self.instance.repetition)
        # self.create_task(project.id)
        project.save()

        models.BoomerangLog.objects.create(project_id=project.group_id, min_rating=project.min_rating,
                                           rating_updated_at=project.rating_updated_at, reason='DEFAULT')

        return project

    def update(self, *args, **kwargs):
        self.instance.name = self.validated_data.get('name', self.instance.name)
        self.instance.price = self.validated_data.get('price', self.instance.price)
        self.instance.has_review = self.validated_data.get('has_review', self.instance.has_review)
        review_project = self.instance.projects.all().filter(is_review=True).first()
        if review_project is not None:
            review_project.price = self.validated_data.get('review_price', review_project.price)
            review_project.save()
        self.instance.repetition = self.validated_data.get('repetition', self.instance.repetition)
        self.instance.deadline = self.validated_data.get('deadline', self.instance.deadline)
        self.instance.timeout = self.validated_data.get('timeout', self.instance.timeout)
        self.instance.post_mturk = self.validated_data.get('post_mturk', self.instance.post_mturk)
        self.instance.qualification = self.validated_data.get('qualification', self.instance.qualification)

        self.instance.save()
        return self.instance

    def update_status(self, *args, **kwargs):
        status = self.initial_data.get('status', self.instance.status)
        validator = ProjectValidator()
        validator.set_context(self)
        validator.__call__(value={'status': status})
        self.instance.status = status
        mturk_update_status.delay({'id': self.instance.id, 'status': status})
        self.instance.save()
        return self.instance

    @staticmethod
    def get_age(model):
        from crowdsourcing.utils import get_relative_time

        if model.status == models.Project.STATUS_DRAFT:
            return get_relative_time(model.updated_at)
        else:
            return get_relative_time(model.published_at)

    @staticmethod
    def get_total_tasks(obj):
        return obj.tasks.all().count()

    @staticmethod
    def get_has_comments(obj):
        return obj.comments.count() > 0

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

    @staticmethod
    def has_csv_linkage(items):
        if items.count() > 0:
            template_items = items.all()
            for item in template_items:
                attribs = item.aux_attributes
                if 'question' in attribs and 'data_source' in attribs['question'] and \
                        attribs['question']['data_source'] is not None:
                    return True

                if 'options' in attribs and attribs['options'] is not None:
                    for option in attribs['options']:
                        if 'data_source' in option and option['data_source'] is not None:
                            return True
        return False

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
        batch_files = self.instance.batch_files.all()

        project = self.instance
        project.name += ' (copy)'
        project.status = models.Project.STATUS_DRAFT
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
        project.group_id = project.id
        project.save()

        for batch_file in batch_files:
            project_batch_file = models.ProjectBatchFile(project=project, batch_file=batch_file)
            project_batch_file.save()

        review_project_name = "Peer Review for " + project.name
        review_project = models.Project.objects.create(name=review_project_name, owner=project.owner,
                                                       parent=project, is_prototype=False,
                                                       is_review=True)

        template = {
            "name": 't_' + generate_random_id(),
            "items": []
        }
        template_serializer = TemplateSerializer(data=template)
        if template_serializer.is_valid():
            review_template = template_serializer.create(with_defaults=False, is_review=True,
                                                         owner=project.owner)
            review_project.template = review_template
        else:
            raise ValidationError(template_serializer.errors)
        review_project.group_id = review_project.id
        review_project.save()
        return project

    @staticmethod
    def create_revision(instance):
        review_project = instance.projects.filter(is_review=True).first()
        models.Project.objects.filter(group_id=instance.group_id).update(status=models.Project.STATUS_PAUSED)
        template = TemplateSerializer.create_revision(instance=instance.template)
        # batch_files = copy.copy(instance.batch_files.all())
        tasks = copy.copy(instance.tasks.all())
        mturk_update_status.delay({'id': instance.id, 'status': models.Project.STATUS_PAUSED})
        instance.pk = None
        instance.template = template
        instance.status = models.Project.STATUS_DRAFT
        instance.is_prototype = False
        instance.is_paid = False
        instance.save()
        # for f in batch_files:
        #     models.ProjectBatchFile.objects.create(project=instance, batch_file=f)

        for t in tasks:
            t.pk = None
            t.project = instance
        TaskSerializer.bulk_create(data=tasks)

        if review_project is not None:
            review_project.parent = instance
            review_project.save()

        return instance

    def publish(self, amount_due):
        validator = ProjectValidator()
        validator.set_context(self)
        validator.__call__(value={'status': models.Project.STATUS_IN_PROGRESS})
        self.instance.repetition = self.validated_data.get('repetition', self.instance.repetition)
        self.instance.published_at = timezone.now()
        if self.instance.has_review:
            review_project = self.instance.projects.filter(is_review=True).first()
            if review_project is not None:
                review_project.status = models.Project.STATUS_IN_PROGRESS
                review_project.name = 'Peer Review for ' + self.instance.name
                review_project.published_at = timezone.now()
                review_project.save()

        status = models.Project.STATUS_IN_PROGRESS

        if status != self.instance.status \
            and status in (models.Project.STATUS_PAUSED, models.Project.STATUS_IN_PROGRESS) and \
                self.instance.status in (models.Project.STATUS_PAUSED, models.Project.STATUS_IN_PROGRESS):
            mturk_update_status.delay({'id': self.instance.id, 'status': status})
        self.instance.status = status
        # TODO rm when mturk is removed if status == models.Project.STATUS_IN_PROGRESS and not self.instance.is_paid:
        #     self.pay(amount_due)
        self.instance.save()

    @staticmethod
    def get_relaunch(obj):
        """
            Not used since we removed csv
        Args:
            obj: project instance

        Returns:

        """
        previous_revision = models.Project.objects.prefetch_related('batch_files').filter(~Q(id=obj.id),
                                                                                          group_id=obj.group_id) \
            .order_by('-id').first()
        previous_batch_file = previous_revision.batch_files.first() if previous_revision else None
        batch_file = obj.batch_files.first()
        active_workers = models.TaskWorker.objects.active().filter(task__project__group_id=obj.group_id,
                                                                   task__exclude_at__isnull=True,
                                                                   status__in=[models.TaskWorker.STATUS_IN_PROGRESS,
                                                                               models.TaskWorker.STATUS_SUBMITTED,
                                                                               models.TaskWorker.STATUS_RETURNED,
                                                                               models.TaskWorker.STATUS_ACCEPTED]
                                                                   ).count()
        same_file = (
            previous_batch_file is not None and batch_file is not None and
            previous_batch_file.id == batch_file.id
        )
        different_file = (previous_batch_file is not None and batch_file is None) or \
                         (previous_batch_file is None and batch_file is not None)
        if previous_revision is None or active_workers == 0:
            return {
                "is_forced": False,
                "ask_for_relaunch": False,
                "overlaps": False
            }
        elif (previous_batch_file is None and batch_file is None) or same_file:
            return {
                "is_forced": False,
                "ask_for_relaunch": True,
                "overlaps": True
            }
        elif different_file:
            return {
                "is_forced": True,
                "ask_for_relaunch": False,
                "overlaps": False
            }
        elif previous_batch_file.id != batch_file.id:
            return {
                "is_forced": False,
                "ask_for_relaunch": True,
                "overlaps": True
            }

    def pay(self, amount_due, *args, **kwargs):
        requester_account = models.FinancialAccount.objects.get(owner_id=self.instance.owner_id,
                                                                type=models.FinancialAccount.TYPE_REQUESTER,
                                                                is_system=False).id
        system_account = models.FinancialAccount.objects.get(is_system=True,
                                                             type=models.FinancialAccount.TYPE_ESCROW).id
        transaction_data = {
            'sender': requester_account,
            'recipient': system_account,
            'amount': amount_due,
            'method': 'daemo',
            'sender_type': models.Transaction.TYPE_PROJECT_OWNER,
            'reference': 'P#' + str(self.instance.id)
        }
        if amount_due < 0:
            transaction_data['sender'] = system_account
            transaction_data['recipient'] = requester_account
            transaction_data['amount'] = abs(amount_due)

        transaction_serializer = TransactionSerializer(data=transaction_data)
        if transaction_serializer.is_valid():
            if amount_due != 0:
                transaction_serializer.create()
            self.instance.is_paid = True
            self.instance.save()
        else:
            raise ValidationError('Error in payment')

    @staticmethod
    def get_revisions(obj):
        return models.Project.objects.active().filter(group_id=obj.group_id).values_list('id', flat=True)

    def reset_boomerang(self):
        update_project_boomerang.delay(self.instance.id)

    @staticmethod
    def get_hash_id(obj):
        return to_hash(obj.group_id)


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
