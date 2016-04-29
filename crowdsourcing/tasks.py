from csp.celery import app as celery_app
from django.db import connection
from crowdsourcing.models import TaskWorker


@celery_app.task
def expire_tasks():
    cursor = connection.cursor()
    query = '''
            WITH taskworkers AS (
                SELECT
                  tw.id
                FROM crowdsourcing_taskworker tw
                INNER JOIN crowdsourcing_task t ON  tw.task_id = t.id
                INNER JOIN crowdsourcing_project p ON t.project_id = p.id
                WHERE p.timeout IS NOT NULL AND tw.created_timestamp + p.timeout * INTERVAL '1 minute' < NOW()
                AND tw.task_status=%(in_progress)s)
                UPDATE crowdsourcing_taskworker tw_up SET task_status=%(expired)s
            FROM taskworkers
            WHERE taskworkers.id=tw_up.id
        '''
    cursor.execute(query, {'in_progress': TaskWorker.STATUS_IN_PROGRESS, 'expired': TaskWorker.STATUS_EXPIRED})
    return 'SUCCESS'
