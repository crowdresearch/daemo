from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models

from crowdsourcing.models import Task, TaskWorker


class MTurkHIT(models.Model):
    STATUS_IN_PROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_EXPIRED = 3

    STATUS = (
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_EXPIRED, 'Expired'),
    )

    hit_id = models.TextField(max_length=256)
    hit_type_id = models.TextField(max_length=256, default='')
    hit_group_id = models.TextField(max_length=128, default='')
    num_assignments = models.IntegerField(default=1)
    task = models.OneToOneField(Task, related_name='mturk_hit', on_delete=models.CASCADE)
    status = models.IntegerField(default=STATUS_IN_PROGRESS, choices=STATUS)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class MTurkAssignment(models.Model):
    hit = models.ForeignKey(MTurkHIT, related_name='mturk_assignments')
    assignment_id = models.TextField(max_length=128)
    status = models.IntegerField(choices=TaskWorker.STATUS, default=TaskWorker.STATUS_IN_PROGRESS)
    task_worker = models.ForeignKey(TaskWorker, related_name='mturk_assignments', on_delete=models.CASCADE, null=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class MTurkNotification(models.Model):
    data = JSONField(null=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class MTurkAccount(models.Model):
    user = models.OneToOneField(User, related_name='mturk_account')
    client_id = models.CharField(max_length=64, null=True, blank=True)
    client_secret = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=128, null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
