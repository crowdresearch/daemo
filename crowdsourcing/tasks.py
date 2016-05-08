import random

from django.conf import settings

from django.db.models import Sum, F, Q, IntegerField

from crowdsourcing import models
from csp.celery import app as celery_app


@celery_app.task
def monitor_tasks_for_review():
    # Worker with num_tasks_post_review + num_reviews_post_review >= NUM_TASKS_FOR_REVIEW
    workers = models.Worker.objects.annotate(
        num_completed_tasks=Sum(F('num_tasks_post_review') + F('num_reviews_post_review'),
                                output_field=IntegerField())) \
        .filter(num_completed_tasks__gte=settings.NUM_TASKS_FOR_REVIEW)

    for worker in workers:
        task_worker_results = models.TaskWorkerResult.objects \
            .filter(task_worker__worker=worker) \
            .filter(
                Q(task_worker__task_status=models.TaskWorker.STATUS_ACCEPTED) | Q(
                    task_worker__task_status=models.TaskWorker.STATUS_REJECTED)) \
            .order_by('-last_updated')[:worker.num_tasks_post_review]

        review_results = models.Review.objects \
            .filter(reviewer=worker, parent__isnull=True) \
            .order_by('-last_updated')[:worker.num_reviews_post_review]

        # choose 1 randomly
        merged = list(task_worker_results) + list(review_results)
        result = random.choice(merged)

        # create review without reviewer - ready for assignment
        if result.__class__.__name__ == 'TaskWorkerResult':
            models.Review.objects.create(
                task_worker_result=result,
                level=result.task_worker.worker.level
            )

        if result.__class__.__name__ == 'Review':
            models.Review.objects.create(
                task_worker_result=result.task_worker_result,
                parent=result,
                level=result.reviewer.level
            )

        worker.num_tasks_post_review = 0
        worker.num_reviews_post_review = 0
        worker.save()

    return {'message': 'SUCCESS'}


@celery_app.task
def monitor_reviews_for_leveling():
    # Worker with num_reviews_post_leveling >= NUM_REVIEWS_FOR_LEVELING
    workers = models.Worker.objects.filter(num_reviews_post_leveling__gte=settings.NUM_REVIEWS_FOR_LEVELING)

    for worker in workers:
        review_results = models.Review.objects \
            .filter(status=models.Review.STATUS_SUBMITTED) \
            .filter(
                Q(task_worker_result__task_worker__worker=worker) | Q(reviewer=worker, parent__isnull=False)) \
            .order_by('-last_updated')[:worker.num_reviews_post_leveling]

        # calculate moving average
        avg = reduce(lambda x, y: x.rating + y.rating, review_results) / len(review_results)

        level = worker.level

        # leveling
        if avg < 1.1:
            level -= 1
        if avg > 3.9:
            level += 2
        else:
            if avg > 3:
                level += 1

        # message = "worker level updated from %d to %d" %(worker.level, level)

        worker.level = level
        worker.num_reviews_post_leveling = 0
        worker.save()

    return {'message': 'SUCCESS'}
