from crowdsourcing.models import Project
from csp.celery import app as celery_app
from csp.settings import SITE_HOST
from mturk.interface import MTurkProvider


@celery_app.task
def mturk_publish():
    provider = MTurkProvider(SITE_HOST)
    projects = Project.objects.filter(deleted=False, min_rating__lt=0.61)
    for project in projects:
        provider.create_hits(project)
    return {'message': 'SUCCESS'}


@celery_app.task
def mturk_hit_update(task):
    provider = MTurkProvider(SITE_HOST)
    return provider.update_max_assignments(task)


@celery_app.task
def mturk_approve(list_workers):
    provider = MTurkProvider(SITE_HOST)
    for task_worker_id in list_workers:
        provider.approve_assignment({'id': task_worker_id})
    return 'SUCCESS'
