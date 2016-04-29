from csp.celery import app as celery_app
from csp.settings import TASK_EXPIRATION_INTERVAL
from crowdsourcing.models import TaskWorker
from datetime import datetime, timedelta


@celery_app.task
def expire_tasks():
    TaskWorker.objects.filter(
        created_timestamp__lte=datetime.utcnow() -
        timedelta(minutes=TASK_EXPIRATION_INTERVAL)).filter(
        task_status=TaskWorker.STATUS_IN_PROGRESS).update(
        task_status=TaskWorker.STATUS_EXPIRED)
    return 'SUCCESS'
