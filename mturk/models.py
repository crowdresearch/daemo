from __future__ import unicode_literals

from django.db import models
from crowdsourcing.models import Task, TaskWorker


class MTurkHIT(models.Model):
    hit_id = models.TextField(max_length=256)
    hit_type_id = models.TextField(max_length=256, null=True)
    task = models.ForeignKey(Task, related_name='mturk_task', on_delete=models.CASCADE)
    is_expired = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class MTurkAssignment(models.Model):
    task = models.ForeignKey(MTurkHIT, related_name='hit_assignments')
    assignment_id = models.TextField(max_length=128)
    worker_id = models.TextField(max_length=128)
    status = models.IntegerField(choices=TaskWorker.STATUS, default=TaskWorker.STATUS_SUBMITTED)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
