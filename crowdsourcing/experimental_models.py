from django.db import models
from django.contrib.postgres.fields import ArrayField
from crowdsourcing.models import Requester, Worker, Module, TaskWorker


class RequesterExperiment(models.Model):
    requester = models.ForeignKey(Requester, related_name='requester_experiment')
    has_prototype = models.BooleanField(default=True)
    has_boomerang = models.BooleanField(default=True)
    pool = models.IntegerField(default=0)


class WorkerExperiment(models.Model):
    worker = models.ForeignKey(Worker, related_name='worker_experiment')
    has_prototype = models.BooleanField(default=True)
    sorting_type = models.IntegerField(default=1)  # 1 boomerang 2 published date
    is_subject_to_cascade = models.BooleanField(default=True)
    feedback_required = models.BooleanField(default=False)
    pool = models.IntegerField(default=0)


class ModulePool(models.Model):
    module = models.ForeignKey(Module, related_name='module_pool')
    pool = models.IntegerField(default=0) # 0-Proto 1-BoomerangWorker 2-BoomerangRequester

class SubModule(models.Model):
    fake_module = models.ForeignKey(Module, related_name='fake_module')
    origin_module = models.ForeignKey(Module, related_name='origin_module')
    owner = models.ForeignKey(RequesterExperiment)
    round_exp = models.IntegerField(default=1) # 1 random sampling, 2 and 3 sample based on ratings
    results_per_round = models.IntegerField(default=1)
    hours_before_results = models.IntegerField(default=1)
    taskworkers = ArrayField(models.IntegerField(), default=list())
    created_timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)