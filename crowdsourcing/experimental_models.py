from django.db import models
from crowdsourcing.models import Requester, Worker, Module


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
    pool = models.IntegerField(default=0)


class ModulePool(models.Model):
    module = models.ForeignKey(Module, related_name='module_pool')
    pool = models.IntegerField(default=0) # 0-Proto 1-BoomerangWorker 2-BoomerangRequester
