from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models

from crowdsourcing.models import Task, TaskWorker


class Timed(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True


class MTurkHIT(Timed):
    STATUS_IN_PROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_EXPIRED = 3
    STATUS_DELETED = 4

    STATUS = (
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_DELETED, 'Deleted')
    )

    hit_id = models.TextField(max_length=256)
    hit_type = models.ForeignKey('MTurkHITType')
    hit_group_id = models.TextField(max_length=128, default='')
    num_assignments = models.IntegerField(default=1)
    task = models.OneToOneField(Task, related_name='mturk_hit', on_delete=models.CASCADE)
    status = models.IntegerField(default=STATUS_IN_PROGRESS, choices=STATUS)


class MTurkAssignment(Timed):
    hit = models.ForeignKey(MTurkHIT, related_name='mturk_assignments')
    assignment_id = models.TextField(max_length=128)
    status = models.IntegerField(choices=TaskWorker.STATUS, default=TaskWorker.STATUS_IN_PROGRESS)
    task_worker = models.ForeignKey(TaskWorker, related_name='mturk_assignments', on_delete=models.CASCADE, null=True)


class MTurkNotification(Timed):
    data = JSONField(null=True)


class MTurkAccount(Timed):
    user = models.OneToOneField(User, related_name='mturk_account')
    client_id = models.CharField(max_length=64, null=True, blank=True)
    client_secret = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=128, null=True, blank=True)
    is_valid = models.BooleanField(default=True)


class MTurkHITType(Timed):
    string_id = models.CharField(max_length=64, null=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=512, blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    keywords = ArrayField(models.CharField(max_length=128), null=True, default=[])
    duration = models.DurationField(null=True)
    qualifications_mask = models.IntegerField(default=0)
    boomerang_qualification = models.ForeignKey('MTurkQualification', null=True)
    boomerang_threshold = models.IntegerField()
    owner = models.ForeignKey(User, related_name='mturk_hit_types')


class MTurkQualification(Timed):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    status = models.CharField(max_length=16, default='Active')
    keywords = ArrayField(models.CharField(max_length=128), null=True, default=[])
    auto_granted = models.BooleanField(default=False)
    auto_granted_value = models.IntegerField(default=1, null=True)
    type_id = models.CharField(max_length=128)
    flag = models.IntegerField()
    owner = models.ForeignKey(User, related_name='mturk_qualifications')
    lower_bound = models.IntegerField(default=100)
    upper_bound = models.IntegerField(default=300)
    is_blacklist = models.BooleanField(default=False)

    class Meta:
        unique_together = ('owner', 'flag', 'name')


class MTurkWorkerQualification(Timed):
    qualification = models.ForeignKey(MTurkQualification)
    worker = models.CharField(max_length=32)
    score = models.IntegerField(default=1)
    overwritten = models.BooleanField(default=False)
