from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
import json
from crowdsourcing.serializers.template import TemplateSerializer
from crowdsourcing.serializers.task import TaskSerializer, TaskCommentSerializer
from rest_framework.exceptions import ValidationError
from crowdsourcing.serializers.requester import RequesterSerializer
from django.utils import timezone
from crowdsourcing.serializers.message import CommentSerializer
from django.db.models import F, Count, Q
from crowdsourcing.utils import get_model_or_none


class CategorySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'parent')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.parent = validated_data.get('parent', instance.parent)
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance


class ModuleSerializer(DynamicFieldsModelSerializer):
    deleted = serializers.BooleanField(read_only=True)
    template = TemplateSerializer(many=True)
    total_tasks = serializers.SerializerMethodField()
    file_id = serializers.IntegerField(write_only=True, allow_null=True)
    age = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()
    available_tasks = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    # comments = TaskCommentSerializer(many=True, source='module_tasks__task_workers__taskcomment_task', read_only=True)

    class Meta:
        model = models.Module
        fields = ('id', 'name', 'owner', 'project', 'description', 'status', 'repetition', 'module_timeout',
                  'deleted', 'template', 'created_timestamp', 'last_updated', 'price', 'has_data_set',
                  'data_set_location', 'total_tasks', 'file_id', 'age', 'is_micro', 'is_prototype', 'task_time',
                  'allow_feedback', 'feedback_permissions', 'min_rating', 'has_comments', 'available_tasks', 'comments')
        read_only_fields = (
            'created_timestamp', 'last_updated', 'deleted', 'owner', 'has_comments', 'available_tasks', 'comments')

    def create(self, **kwargs):
        templates = self.validated_data.pop('template')
        project = self.validated_data.pop('project')
        file_id = self.validated_data.pop('file_id')
        csv_data = []
        if file_id is not None:
            uploaded_file = models.RequesterInputFile.objects.get(id=file_id)
            csv_data = uploaded_file.parse_csv()
            uploaded_file.delete()

        # module_tasks = self.validated_data.pop('module_tasks')
        module = models.Module.objects.create(deleted=False, project=project,
                                              owner=kwargs['owner'].requester, **self.validated_data)

        for template in templates:
            template_items = template.pop('template_items')
            t = models.Template.objects.get_or_create(owner=kwargs['owner'], **template)
            models.ModuleTemplate.objects.get_or_create(module=module, template=t[0])
            for item in template_items:
                models.TemplateItem.objects.get_or_create(template=t[0], **item)
        if module.has_data_set:
            for row in csv_data:
                task = {
                    'module': module.id,
                    'data': json.dumps(row)
                }
                task_serializer = TaskSerializer(data=task)
                if task_serializer.is_valid():
                    task_serializer.create(**kwargs)
                else:
                    raise ValidationError(task_serializer.errors)
        else:
            task = {
                'module': module.id,
                'data': "{\"type\": \"static\"}"
            }
            task_serializer = TaskSerializer(data=task)
            if task_serializer.is_valid():
                task_serializer.create(**kwargs)
            else:
                raise ValidationError(task_serializer.errors)
        return module

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

    def get_age(self, model):
        from crowdsourcing.utils import get_time_delta

        delta = get_time_delta(model.created_timestamp)

        return "Posted " + delta

    def get_total_tasks(self, obj):
        return obj.module_tasks.all().count()

    def get_has_comments(self, obj):
        return obj.modulecomment_module.count() > 0

    def get_available_tasks(self, obj):
        available_task_count = models.Module.objects.values('id').raw('''
          select count(*) id from (
            SELECT
              "crowdsourcing_task"."id"
            FROM "crowdsourcing_task"
              INNER JOIN "crowdsourcing_module" ON ("crowdsourcing_task"."module_id" = "crowdsourcing_module"."id")
              LEFT OUTER JOIN "crowdsourcing_taskworker" ON ("crowdsourcing_task"."id" =
                "crowdsourcing_taskworker"."task_id" and task_status not in (4,6))
            WHERE ("crowdsourcing_task"."module_id" = %s AND NOT (
              ("crowdsourcing_task"."id" IN (SELECT U1."task_id" AS Col1
              FROM "crowdsourcing_taskworker" U1 WHERE U1."worker_id" = %s and U1.task_status<>6))))
            GROUP BY "crowdsourcing_task"."id", "crowdsourcing_module"."repetition"
            HAVING "crowdsourcing_module"."repetition" > (COUNT("crowdsourcing_taskworker"."id"))) available_tasks
            ''', params=[obj.id, self.context['request'].user.userprofile.worker.id])[0].id
        return available_task_count

    def get_comments(self, obj):
        if obj:
            comments = []
            tasks = obj.module_tasks.all()
            for task in tasks:
                task_comments = task.taskcomment_task.all()
                for task_comment in task_comments:
                    comments.append(task_comment)
            serializer = TaskCommentSerializer(many=True, instance=comments, read_only=True)
            return serializer.data
        return []


class ProjectSerializer(DynamicFieldsModelSerializer):
    deleted = serializers.BooleanField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all(), many=True)
    owner = RequesterSerializer(read_only=True)
    module_count = serializers.SerializerMethodField()
    modules = ModuleSerializer(many=True, fields=('id', 'name', 'description', 'status', 'repetition', 'module_timeout',
                                                  'price', 'template', 'total_tasks', 'file_id', 'has_data_set', 'age',
                                                  'is_micro', 'is_prototype', 'task_time', 'has_comments',
                                                  'allow_feedback', 'feedback_permissions', 'available_tasks'))
    modules_filtered = serializers.SerializerMethodField()

    class Meta:
        model = models.Project
        fields = ('id', 'name', 'owner', 'description', 'deleted',
                  'categories', 'modules', 'module_count', 'modules_filtered')

    def create(self, **kwargs):
        categories = self.validated_data.pop('categories')
        modules = self.validated_data.pop('modules')
        project = models.Project.objects.create(owner=kwargs['owner'].requester, deleted=False, **self.validated_data)
        for category in categories:
            models.ProjectCategory.objects.create(project=project, category=category)
        for module in modules:
            module['project'] = project.id
            module_serializer = ModuleSerializer(data=module)
            if module_serializer.is_valid():
                module_serializer.create(owner=kwargs['owner'])
            else:
                raise ValidationError(module_serializer.errors)
        return project

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

    def get_module_count(self, obj):
        return obj.modules.all().count()


class ProjectRequesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectRequester


class ModuleReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModuleReview
        fields = ('id', 'worker', 'annonymous', 'module', 'comments')
        read_only_fields = ('last_updated')


class ModuleRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModuleRating
        fields = ('id', 'worker', 'module', 'value')
        read_only_fields = ('last_updated')


class WorkerModuleApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerModuleApplication


class QualificationApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification


class QualificationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QualificationItem


class BookmarkedProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BookmarkedProjects
        fields = ('id', 'project')

    def create(self, **kwargs):
        models.BookmarkedProjects.objects.get_or_create(profile=kwargs['profile'], **self.validated_data)


class ModuleCommentSerializer(DynamicFieldsModelSerializer):
    comment = CommentSerializer()

    class Meta:
        model = models.ModuleComment
        fields = ('id', 'module', 'comment')
        read_only_fields = ('module',)

    def create(self, **kwargs):
        comment_data = self.validated_data.pop('comment')
        comment_serializer = CommentSerializer(data=comment_data)
        if comment_serializer.is_valid():
            comment = comment_serializer.create(sender=kwargs['sender'])
            module_comment = models.ModuleComment.objects.create(module_id=kwargs['module'], comment_id=comment.id)
            return {'id': module_comment.id, 'comment': comment}


'''
class ModuleSerializer(DynamicFieldsModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    num_reviews = serializers.SerializerMethodField()
    num_raters = serializers.SerializerMethodField()
    avg_pay = serializers.SerializerMethodField()
    min_pay = serializers.SerializerMethodField()
    completed_on = serializers.SerializerMethodField()
    total_submissions = serializers.SerializerMethodField()
    num_contributors = serializers.SerializerMethodField()
    num_accepted = serializers.SerializerMethodField()
    num_rejected = serializers.SerializerMethodField()
    total_tasks = serializers.SerializerMethodField()
    average_time = serializers.SerializerMethodField()

    deleted = serializers.BooleanField(read_only=True)
    categories = CategorySerializer(many=True,read_only=True,fields=('id','name'))
    project = ProjectSerializer(many = False, read_only = True, fields=('id','name'))

    def create(self, validated_data):
        categories = validated_data.pop('categories')
        module = models.Module.objects.create(deleted = False,**validated_data)
        for c in categories:
            models.ModuleCategory.objects.create(module=module, category=c)
        return module

    def update(self,instance,validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.keywords = validated_data.get('keywords', instance.keywords)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price',instance.price)
        instance.repetition = validated_data.get('repetition',instance.repetition)
        instance.module_timeout = validated_data.get('module_timeout',instance.module_timeout)
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

    def get_num_reviews(self,model):
        return model.modulereview_set.count()

    def get_num_raters(self,model):
        return model.modulerating_set.count()

    def get_avg_rating(self, model):
        return model.modulerating_set.all().aggregate(avg=Avg('value')).get('avg') # should be updated automatically

    def get_avg_pay(self, model):
        return model.task_set.all().aggregate(avg=Avg('price')).get('avg')

    def get_min_pay(self, model):
        return model.task_set.all().aggregate(min=Min('price')).get('min') # should be updated automatically

    def get_num_accepted(self, model):
        return models.TaskWorkerResult.objects.all().filter(task_worker__task__module = model,status = 2).count()

    def get_num_rejected(self, model):
        return models.TaskWorkerResult.objects.all().filter(task_worker__task__module = model,status = 3).count()

    def get_total_tasks(self, model):
        return model.task_set.all().count()

    def get_completed_on(self, model):
        if model.task_set.all().exclude(status = 4).count()>0:
            return "Not Comlpeted"
        else:
            return model.task_set.all().aggregate(date=Max('last_updated')).get('date').date()

    def get_total_submissions(self, model):
        return models.TaskWorkerResult.objects.all().filter(task_worker__task__module=model).count()

    def get_num_contributors(self,model):
        acceptedTaskWorker = models.TaskWorker.objects.all().filter(task__module = model,taskworkerresult__status = 2)
        return acceptedTaskWorker.order_by('worker').distinct('worker').count()

    def get_average_time(self,model):
        taskworkers = models.TaskWorker.objects.all().filter(task__module = model)
        time_spent = 0
        count = 0
        for taskworker in taskworkers:
            init = taskworker.created_timestamp
            maxend = taskworker.taskworkerresult_set.all().aggregate(max = Max('created_timestamp')).get('max')
            if maxend != None:
                time_spent = time_spent+(((maxend - init).total_seconds())/3600)
                count = count + 1

        return time_spent/count

    class Meta:
        model = models.Module
        fields = ('id', 'name', 'owner', 'project', 'categories', 'description', 'keywords', 'status',
                  'repetition','module_timeout','deleted','created_timestamp','last_updated','avg_rating',
                  'num_reviews','completed_on','total_submissions','num_contributors','num_raters','min_pay','avg_pay','num_accepted','num_rejected','total_tasks','average_time')
        read_only_fields = ('created_timestamp','last_updated')

'''
