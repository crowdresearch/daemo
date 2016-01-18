from __future__ import unicode_literals

from django.db import models
from crowdsourcing.models import Task, TaskWorker


class MTurkHIT(models.Model):
    STATUS_CREATED = 1
    STATUS_COMPLETED = 2
    STATUS_NOT_NEEDED = 3
    STATUS_FORKED = 4

    STATUS = (
        (STATUS_CREATED, 'Created'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_NOT_NEEDED, 'Done on Daemo'),
        (STATUS_FORKED, 'Forked'),
    )

    hit_id = models.TextField(max_length=256)
    hit_type_id = models.TextField(max_length=256, default='')
    hit_group_id = models.TextField(max_length=128, default='')
    task = models.ForeignKey(Task, related_name='mturk_task', on_delete=models.CASCADE)
    status = models.IntegerField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        unique_together = ('task', 'status')


class MTurkAssignment(models.Model):
    hit = models.ForeignKey(MTurkHIT, related_name='hit_assignments')
    assignment_id = models.TextField(max_length=128)
    worker_id = models.TextField(max_length=128)
    status = models.IntegerField(choices=TaskWorker.STATUS, default=TaskWorker.STATUS_SUBMITTED)
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
