from csp.celery import app as celery_app
from django.db import connection
from crowdsourcing.models import TaskWorker
from crowdsourcing.redis import RedisProvider


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
                AND tw.status=%(in_progress)s)
                UPDATE crowdsourcing_taskworker tw_up SET task_status=%(expired)s
            FROM taskworkers
            WHERE taskworkers.id=tw_up.id
            RETURNING tw_up.worker_id
        '''
    cursor.execute(query, {'in_progress': TaskWorker.STATUS_IN_PROGRESS, 'expired': TaskWorker.STATUS_EXPIRED})
    workers = cursor.fetchall()
    worker_list = [w[0] for w in workers]
    update_worker_cache.delay(worker_list, 'EXPIRED')
    return 'SUCCESS'


@celery_app.task
def update_worker_cache(workers, operation, key=None, value=None):
    provider = RedisProvider()

    for worker in workers:
        name = provider.build_key('worker', worker)
        if operation == 'CREATED':
            provider.hincrby(name, 'in_progress', 1)
        elif operation == 'SUBMITTED':
            provider.hincrby(name, 'in_progress', -1)
            provider.hincrby(name, 'submitted', 1)
        elif operation == 'REJECTED':
            provider.hincrby(name, 'submitted', -1)
            provider.hincrby(name, 'rejected', 1)
        elif operation == 'RETURNED':
            provider.hincrby(name, 'submitted', -1)
            provider.hincrby(name, 'returned', 1)
        elif operation == 'APPROVED':
            provider.hincrby(name, 'submitted', -1)
            provider.hincrby(name, 'approved', 1)
        elif operation in ['EXPIRED', 'SKIPPED']:
            provider.hincrby(name, 'in_progress', -1)
        elif operation == 'GROUPADD':
            provider.set_add(name + ':worker_groups', value)
        elif operation == 'UPDATE_PROFILE':
            provider.set_hash(name, key, value)

    return 'SUCCESS'
