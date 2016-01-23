from crowdsourcing.models import Project
from csp.celery import app as celery_app
from csp.settings import SITE_HOST
from mturk.interface import MTurkProvider


@celery_app.task
def mturk_publish():
    provider = MTurkProvider(SITE_HOST)
    projects = Project.objects.filter(deleted=False, min_rating=0)
    for project in projects:
        provider.create_hits(project)
    return {'message': 'SUCCESS'}


@celery_app.task
def mturk_hit_update(task):
    provider = MTurkProvider(SITE_HOST)
    return provider.update_max_assignments(task)
