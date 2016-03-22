from crowdsourcing.models import Project, TaskWorker, Task
from csp.celery import app as celery_app
from csp.settings import SITE_HOST, AWS_DAEMO_KEY, MTURK_THRESHOLD
from mturk.interface import MTurkProvider
from mturk.models import MTurkHIT
from django.db.models import Q
from django.contrib.auth.models import User
from crowdsourcing.crypto import AESUtil


@celery_app.task
def mturk_publish():
    projects = Project.objects.filter(~Q(owner__profile__user__mturk_account=None), deleted=False,
                                      min_rating__lt=MTURK_THRESHOLD,
                                      post_mturk=True)
    for project in projects:
        provider = get_provider(project.owner.profile.user)
        provider.create_hits(project)
    return {'message': 'SUCCESS'}


@celery_app.task
def mturk_hit_update(task):
    user_id = Task.objects.values('project__owner__profile__user').get(id=task['id'])['project__owner__profile__user']
    user = User.objects.get(id=user_id)
    provider = get_provider(user)
    if provider is None:
        return
    return provider.update_max_assignments(task)


@celery_app.task
def mturk_approve(list_workers):
    user_id = TaskWorker.objects.values('task__project__owner__profile__user').get(
        id=list_workers[0])['task__project__owner__profile__user']
    user = User.objects.get(id=user_id)
    provider = get_provider(user)
    if provider is None:
        return
    for task_worker_id in list_workers:
        provider.approve_assignment({'id': task_worker_id})
    return 'SUCCESS'


@celery_app.task
def mturk_update_status(project):
    user_id = Project.objects.values('owner__profile__user').get(id=project['id'])['owner__profile__user']
    user = User.objects.get(id=user_id)
    provider = get_provider(user)
    if provider is None:
        return
    hits = MTurkHIT.objects.filter(task__project_id=project['id'])
    for hit in hits:
        if project['status'] == Project.STATUS_IN_PROGRESS:
            provider.extend_hit(hit.hit_id)
            hit.status = MTurkHIT.STATUS_IN_PROGRESS
        else:
            provider.expire_hit(hit.hit_id)
            hit.status = MTurkHIT.STATUS_EXPIRED
        hit.save()
    return 'SUCCESS'


def get_provider(user, host=None):
    if not hasattr(user, 'mturk_account'):
        return None
    if host is None:
        host = SITE_HOST
    client_secret = AESUtil(key=AWS_DAEMO_KEY).decrypt(user.mturk_account.client_secret)
    return MTurkProvider(host=host, aws_access_key_id=user.mturk_account.client_id,
                         aws_secret_access_key=client_secret)
