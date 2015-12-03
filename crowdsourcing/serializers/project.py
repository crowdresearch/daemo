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


class ProjectSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Project
        fields = ('id', 'name')

    def create(self, **kwargs):
        create_module = kwargs['create_module']
        project = models.Project.objects.create(owner=kwargs['owner'].requester, deleted=False, **self.validated_data)
        response_data = project
        if create_module:
            response_data = models.Module.objects.create(project=project, owner=kwargs['owner'].requester)
        return response_data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance


class ModuleSerializer(DynamicFieldsModelSerializer):
    deleted = serializers.BooleanField(read_only=True)
    template = TemplateSerializer(many=True)
    # TODO finish backend for module
    total_tasks = serializers.SerializerMethodField()
    file_id = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    age = serializers.SerializerMethodField()
    has_comments = serializers.SerializerMethodField()
    available_tasks = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    name = serializers.CharField(default='Untitled Milestone')
    status = serializers.IntegerField(default=1)
    project = serializers.SerializerMethodField()

    # comments = TaskCommentSerializer(many=True, source='module_tasks__task_workers__taskcomment_task', read_only=True)

    class Meta:
        model = models.Module
        fields = ('id', 'name', 'owner', 'project', 'description', 'status', 'repetition', 'timeout',
                  'template',
                  'deleted', 'created_timestamp', 'last_updated', 'price', 'has_data_set',
                  'data_set_location', 'total_tasks', 'file_id', 'age', 'is_micro', 'is_prototype', 'task_time',
                  'allow_feedback', 'feedback_permissions', 'min_rating', 'has_comments', 'available_tasks', 'comments',)
        read_only_fields = (
            'created_timestamp', 'last_updated', 'deleted', 'owner', 'has_comments', 'available_tasks',
            'comments')

    def create(self, **kwargs):
        project = self.validated_data.pop('project')
        file_id = None
        csv_data = []
        if file_id is not None:
            uploaded_file = models.RequesterInputFile.objects.get(id=file_id)
            csv_data = uploaded_file.parse_csv()

        module = models.Module.objects.create(deleted=False, project=project,
                                              owner=kwargs['owner'].requester, **self.validated_data)

        template = {
            "name": "t_Q7AAC9"
        }
        t = models.Template.objects.get_or_create(owner=kwargs['owner'], **template)
        models.ModuleTemplate.objects.get_or_create(module=module, template=t[0])
        item = {
            "type": "radio",
            "values": "Option 1,Option 2,Option 3",
            "label": "Add question here",
            "data_source": None,
            "layout": "row",
            "id_string": "radio_0",
            "name": "radio_0",
            "icon": "radio_button_checked",
            "position": 1
        }
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

    def get_project(self, obj):
        project = {
            "id": obj.project.id,
            "name": obj.project.name
        }
        return project


class ProjectRequesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectRequester


class ModuleReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModuleReview
        fields = ('id', 'worker', 'annonymous', 'module', 'comments')
        read_only_fields = ('last_updated',)


class ModuleRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ModuleRating
        fields = ('id', 'worker', 'module', 'value')
        read_only_fields = ('last_updated',)


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
