import json
import random

from django.conf import settings

from django.db.models import Sum, F, Q, IntegerField
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

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
        task_workers = models.TaskWorker.objects \
            .filter(worker=worker) \
            .filter(
                Q(task_status=models.TaskWorker.STATUS_ACCEPTED) | Q(
                    task_status=models.TaskWorker.STATUS_REJECTED)) \
            .order_by('-last_updated')[:worker.num_tasks_post_review]

        reviews = models.Review.objects \
            .filter(reviewer=worker, parent__isnull=True) \
            .order_by('-last_updated')[:worker.num_reviews_post_review]

        # choose 1 randomly
        merged = list(task_workers) + list(reviews)
        result = random.choice(merged)

        # create review without reviewer - ready for assignment
        if result.__class__.__name__ == 'TaskWorker':
            models.Review.objects.create(
                task_worker=result,
                level=result.worker.level,
                time_spent=0
            )

        if result.__class__.__name__ == 'Review':
            models.Review.objects.create(
                task_worker=result.task_worker,
                parent=result,
                level=result.reviewer.level,
                time_spent=0
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
        reviews = models.Review.objects \
            .filter(status=models.Review.STATUS_SUBMITTED) \
            .filter(
                Q(task_worker__worker=worker) | Q(reviewer=worker, parent__isnull=False)) \
            .order_by('-last_updated')[:settings.NUM_REVIEWS_FOR_LEVELING]

        # calculate moving average
        avg = reduce(lambda x, y: x.rating + y.rating, reviews) / len(reviews)

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
        if level != worker.level:
            redis_publisher = RedisPublisher(facility='notifications', users=[worker.profile.user])
            message = RedisMessage(json.dumps({"level": True}))
            redis_publisher.publish_message(message)

            worker.level = level
            worker.num_reviews_post_leveling = 0
            worker.save()

    return {'message': 'SUCCESS'}
