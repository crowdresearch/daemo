from csp.celery import app as celery_app
from crowdsourcing.models import Worker, TaskWorker


@celery_app.task
def pay_workers():
    workers = Worker.objects.filter(id=2)
    total = 0
    for worker in workers:
        tasks = TaskWorker.objects.values('task__project__price', 'id').filter(worker=worker,
                                                                               task_status=TaskWorker.STATUS_ACCEPTED,
                                                                               is_paid=False)
        total = sum(tasks.values_list('task__project__price', flat=True))
        if total > 0:
            #  paypal call here
            tasks.update(is_paid=True)

    return {"total": total}
