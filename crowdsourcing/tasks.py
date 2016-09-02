from collections import OrderedDict
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection, transaction
from django.db.models import F, Q
from django.utils import timezone

from crowdsourcing import models
import constants
from crowdsourcing.emails import send_notifications_email
from crowdsourcing.redis import RedisProvider
from crowdsourcing.utils import PayPalBackend, hash_task
from csp.celery import app as celery_app


@celery_app.task(ignore_result=True)
def expire_tasks():
    cursor = connection.cursor()
    # noinspection SqlResolve
    query = '''
            WITH taskworkers AS (
                SELECT
                  tw.id,
                  p.id project_id
                FROM crowdsourcing_taskworker tw
                INNER JOIN crowdsourcing_task t ON  tw.task_id = t.id
                INNER JOIN crowdsourcing_project p ON t.project_id = p.id
                WHERE p.timeout IS NOT NULL AND tw.created_at + p.timeout < NOW()
                AND tw.status=%(in_progress)s)
                UPDATE crowdsourcing_taskworker tw_up SET status=%(expired)s
            FROM taskworkers
            WHERE taskworkers.id=tw_up.id
            RETURNING tw_up.id, tw_up.worker_id
        '''
    cursor.execute(query,
                   {'in_progress': models.TaskWorker.STATUS_IN_PROGRESS, 'expired': models.TaskWorker.STATUS_EXPIRED})
    workers = cursor.fetchall()
    worker_list = []
    task_workers = []
    for w in workers:
        worker_list.append(w[1])
        task_workers.append({'id': w[0]})
    refund_task.delay(task_workers)
    update_worker_cache.delay(worker_list, constants.TASK_EXPIRED)
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def update_worker_cache(workers, operation, key=None, value=None):
    provider = RedisProvider()

    for worker in workers:
        name = provider.build_key('worker', worker)
        if operation == constants.TASK_ACCEPTED:
            provider.hincrby(name, 'in_progress', 1)
        elif operation == constants.TASK_SUBMITTED:
            provider.hincrby(name, 'in_progress', -1)
            provider.hincrby(name, 'submitted', 1)
        elif operation == constants.TASK_REJECTED:
            provider.hincrby(name, 'submitted', -1)
            provider.hincrby(name, 'rejected', 1)
        elif operation == constants.TASK_RETURNED:
            provider.hincrby(name, 'submitted', -1)
            provider.hincrby(name, 'returned', 1)
        elif operation == constants.TASK_APPROVED:
            provider.hincrby(name, 'submitted', -1)
            provider.hincrby(name, 'approved', 1)
        elif operation in [constants.TASK_EXPIRED, constants.TASK_SKIPPED]:
            provider.hincrby(name, 'in_progress', -1)
        elif operation == constants.ACTION_GROUPADD:
            provider.set_add(name + ':worker_groups', value)
        elif operation == constants.ACTION_UPDATE_PROFILE:
            provider.set_hash(name, key, value)

    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def email_notifications():
    users = User.objects.all()
    url = '%s/%s/' % (settings.SITE_HOST, 'messages')
    users_notified = []

    for user in users:
        email_notification, created = models.EmailNotification.objects.get_or_create(recipient=user)

        if created:
            # unread messages
            message_recipients = models.MessageRecipient.objects.filter(
                status__lt=models.MessageRecipient.STATUS_READ,
                recipient=user
            ).exclude(message__sender=user)

        else:
            # unread messages since last notification
            message_recipients = models.MessageRecipient.objects.filter(
                status__lt=models.MessageRecipient.STATUS_READ,
                created_at__gt=email_notification.updated_at,
                recipient=user
            ).exclude(message__sender=user)

        message_recipients = message_recipients.order_by('-created_at') \
            .select_related('message', 'recipient', 'message__sender') \
            .values('created_at', 'message__body', 'recipient__username', 'message__sender__username')

        result = OrderedDict()

        # group messages by sender
        for message_recipient in message_recipients:
            if message_recipient['message__sender__username'] in result:
                result[message_recipient['message__sender__username']].append(message_recipient)
            else:
                result[message_recipient['message__sender__username']] = [message_recipient]

        messages = [{'sender': k, 'messages': v} for k, v in result.items()]

        if len(messages) > 0:
            # send email
            send_notifications_email(email=user.email, url=url, messages=messages)

            users_notified.append(user)

    # update the last time user was notified
    models.EmailNotification.objects.filter(recipient__in=users_notified).update(updated_at=timezone.now())

    return 'SUCCESS'


@celery_app.task(bind=True, ignore_result=True)
def create_tasks(self, tasks):
    try:
        with transaction.atomic():
            task_obj = []
            x = 0
            for task in tasks:
                x += 1
                hash_digest = hash_task(task['data'])
                t = models.Task(data=task['data'], hash=hash_digest, project_id=task['project_id'],
                                row_number=x)
                task_obj.append(t)
            models.Task.objects.bulk_create(task_obj)
            models.Task.objects.filter(project_id=tasks[0]['project_id']).update(group_id=F('id'))
    except Exception as e:
        self.retry(countdown=4, exc=e, max_retries=2)

    return 'SUCCESS'


@celery_app.task(bind=True, ignore_result=True)
def create_tasks_for_project(self, project_id, file_deleted):
    project = models.Project.objects.filter(pk=project_id).first()
    if project is None:
        return 'NOOP'
    previous_rev = models.Project.objects.prefetch_related('batch_files', 'tasks').filter(~Q(id=project.id),
                                                                                          group_id=project.group_id) \
        .order_by('-id').first()

    previous_batch_file = previous_rev.batch_files.first() if previous_rev else None
    models.Task.objects.filter(project=project).delete()
    if file_deleted:
        models.Task.objects.filter(project=project).delete()
        task_data = {
            "project_id": project_id,
            "data": {}
        }
        task = models.Task.objects.create(**task_data)
        if previous_batch_file is None:
            task.group_id = previous_rev.tasks.all().first().group_id
        else:
            task.group_id = task.id
        task.save()
        return 'SUCCESS'
    try:
        with transaction.atomic():
            data = project.batch_files.first().parse_csv()
            task_obj = []
            x = 0
            previous_tasks = previous_rev.tasks.all().order_by('row_number') if previous_batch_file else []
            previous_count = len(previous_tasks)
            for row in data:
                x += 1
                hash_digest = hash_task(row)
                t = models.Task(data=row, hash=hash_digest, project_id=int(project_id), row_number=x)
                if previous_batch_file is not None and x <= previous_count:
                    if len(set(row.items()) ^ set(previous_tasks[x - 1].data.items())) == 0:
                        t.group_id = previous_tasks[x - 1].group_id
                task_obj.append(t)
            models.Task.objects.bulk_create(task_obj)
            models.Task.objects.filter(project_id=project_id, group_id__isnull=True) \
                .update(group_id=F('id'))
    except Exception as e:
        self.retry(countdown=4, exc=e, max_retries=2)

    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def pay_workers():
    workers = User.objects.all()
    total = 0

    for worker in workers:
        tasks = models.TaskWorker.objects.values('task__project__price', 'id') \
            .filter(worker=worker, status=models.TaskWorker.STATUS_ACCEPTED, is_paid=False)
        total = sum(tasks.values_list('task__project__price', flat=True))
        if total > 0 and worker.profile.paypal_email is not None and single_payout(total, worker):
            tasks.update(is_paid=True)

    return {"total": total}


def single_payout(amount, user):
    backend = PayPalBackend()

    payout = backend.paypalrestsdk.Payout({
        "sender_batch_header": {
            "sender_batch_id": "batch_worker_id__" + str(user.id) + '_week__' + str(timezone.now().isocalendar()[1]),
            "email_subject": "Daemo Payment"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": amount,
                    "currency": "USD"
                },
                "receiver": user.profile.paypal_email,
                "note": "Your Daemo payment.",
                "sender_item_id": "item_1"
            }
        ]
    })
    payout_log = models.PayPalPayoutLog()
    payout_log.worker = user
    if payout.create(sync_mode=True):
        payout_log.is_valid = payout.batch_header.transaction_status == 'SUCCESS'
        payout_log.save()
        return payout_log.is_valid
    else:
        payout_log.is_valid = False
        payout_log.response = payout.error
        payout_log.save()
        return False


@celery_app.task(ignore_result=True)
def post_approve(task_id, num_workers):
    task = models.Task.objects.prefetch_related('project').get(pk=task_id)
    latest_revision = models.Project.objects.filter(~Q(status=models.Project.STATUS_DRAFT),
                                                    group_id=task.project.group_id) \
        .order_by('-id').first()
    latest_revision.amount_due -= Decimal(num_workers * task.project.price)
    latest_revision.save()
    return 'SUCCESS'


def create_transaction(sender_id, recipient_id, amount, reference):
    transaction_data = {
        'sender_id': sender_id,
        'recipient_id': recipient_id,
        'amount': amount,
        'method': 'daemo',
        'sender_type': models.Transaction.TYPE_SYSTEM,
        'reference': 'P#' + str(reference)
    }
    with transaction.atomic():
        daemo_transaction = models.Transaction.objects.create(**transaction_data)
        daemo_transaction.recipient.balance += Decimal(daemo_transaction.amount)
        daemo_transaction.recipient.save()
        if daemo_transaction.sender.type not in [models.FinancialAccount.TYPE_WORKER,
                                                 models.FinancialAccount.TYPE_REQUESTER]:
            daemo_transaction.sender.balance -= Decimal(daemo_transaction.amount)
            daemo_transaction.sender.save()
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def refund_task(task_worker_in):
    task_worker_ids = [tw['id'] for tw in task_worker_in]
    system_account = models.FinancialAccount.objects.get(is_system=True,
                                                         type=models.FinancialAccount.TYPE_ESCROW).id
    task_workers = models.TaskWorker.objects.prefetch_related('task', 'task__project').filter(
        id__in=task_worker_ids)
    amount = 0
    for task_worker in task_workers:

        latest_revision = models.Project.objects.filter(~Q(status=models.Project.STATUS_DRAFT),
                                                        group_id=task_worker.task.project.group_id) \
            .order_by('-id').first()
        is_running = latest_revision.deadline is None or latest_revision.deadline > timezone.now()
        if task_worker.task.project_id == latest_revision.id:
            amount = 0
        elif task_worker.task.exclude_at is not None:
            amount = task_worker.task.project.price
        elif is_running and latest_revision.price >= task_worker.task.project.price:
            amount = 0
        elif is_running and latest_revision.price < task_worker.task.project.price:
            amount = task_worker.task.project.price - latest_revision.price
        else:
            amount = latest_revision.price
        if amount > 0:
            requester_account = models.FinancialAccount.objects.get(owner_id=task_worker.task.project.owner_id,
                                                                    type=models.FinancialAccount.TYPE_REQUESTER,
                                                                    is_system=False).id
            create_transaction(sender_id=system_account, recipient_id=requester_account, amount=amount,
                               reference=task_worker.id)
            latest_revision.amount_due -= Decimal(amount)
            latest_revision.save()
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def update_feed_boomerang():
    # TODO fix group_id
    cursor = connection.cursor()
    # noinspection SqlResolve
    query = '''
        WITH boomerang_ratings AS (
            SELECT pid, name, min_rating, tasks_in_progress, task_count,
             CASE WHEN task_count > 0 AND ((tasks_in_progress > 0 AND
               task_count/tasks_in_progress >= (%(BOOMERANG_LAMBDA)s))
               OR tasks_in_progress = 0) THEN min_rating
            WHEN avg_worker_rating <= (%(BOOMERANG_MIDPOINT)s) AND min_rating>(%(BOOMERANG_MIDPOINT)s)
            THEN (%(BOOMERANG_MIDPOINT)s)

            ELSE avg_worker_rating
            END new_min_rating
        FROM (SELECT t.pid, t.name, t.min_rating, t.tasks_in_progress, t.task_count,
               max(t.avg_worker_rating) avg_worker_rating FROM (
            SELECT
              p.id pid,
              p.name,
              p.min_rating,
              p.tasks_in_progress,
              t.task_count,
              coalesce(m.task_w_avg, mp.requester_w_avg, m_platform.platform_w_avg, (%(BOOMERANG_MIDPOINT)s))
               avg_worker_rating
            FROM crowdsourcing_project p
              INNER JOIN (SELECT
                            t.project_id pid,
                            count(tw.id) task_count
                          FROM crowdsourcing_task t
                            LEFT OUTER JOIN crowdsourcing_taskworker tw
                              ON t.id = tw.task_id AND tw.status IN (1, 2, 3, 5)
                                 AND tw.created_at BETWEEN now() -
                                                           ((%(HEART_BEAT_BOOMERANG)s) ||' minute')::INTERVAL AND now()
                          GROUP BY t.project_id) t ON t.pid = p.id
              LEFT OUTER JOIN (
                        SELECT
                          target_id,
                          username,
                          sum(weight * power((%(BOOMERANG_PLATFORM_ALPHA)s), r.row_number))
                          / sum(power((%(BOOMERANG_PLATFORM_ALPHA)s), r.row_number)) platform_w_avg
                        FROM (

                               SELECT
                                 r.id,
                                 u.username                        username,
                                 weight,
                                 r.target_id,
                                 -1 + row_number()
                                 OVER (PARTITION BY worker_id
                                   ORDER BY tw.created_at DESC) AS row_number

                               FROM crowdsourcing_rating r
                                 INNER JOIN crowdsourcing_task t ON t.id = r.task_id
                                 INNER JOIN crowdsourcing_taskworker tw ON t.id = tw.task_id
                                 INNER JOIN auth_user u ON u.id = r.target_id
                               WHERE origin_type = (%(origin_type)s)
                             ) r
                        GROUP BY target_id, username) m_platform ON TRUE
                        --ON m_platform.platform_w_avg < p.min_rating

              LEFT OUTER JOIN (
                               SELECT
                                 target_id,
                                 origin_id,
                                 sum(weight * power((%(BOOMERANG_REQUESTER_ALPHA)s), t.row_number))
                                 / sum(power((%(BOOMERANG_REQUESTER_ALPHA)s), t.row_number)) requester_w_avg
                               FROM (

                                      SELECT
                                        r.id,
                                        r.origin_id,
                                        weight,
                                        r.target_id,
                                        -1 + row_number()
                                        OVER (PARTITION BY worker_id
                                          ORDER BY tw.created_at DESC) AS row_number

                                      FROM crowdsourcing_rating r
                                        INNER JOIN crowdsourcing_task t ON t.id = r.task_id
                                        INNER JOIN crowdsourcing_taskworker tw ON t.id = tw.task_id
                                      WHERE origin_type = (%(origin_type)s)) t
                               GROUP BY origin_id, target_id)
                             mp ON mp.origin_id = p.owner_id
                             AND mp.target_id = m_platform.target_id
                             ---AND mp.requester_w_avg < p.min_rating
              LEFT OUTER JOIN (
                               SELECT
                                 target_id,
                                 origin_id,
                                 project_id,
                                 sum(weight * power((%(BOOMERANG_TASK_ALPHA)s), t.row_number))
                                 / sum(power((%(BOOMERANG_TASK_ALPHA)s), t.row_number)) task_w_avg
                               FROM (

                                      SELECT
                                        r.id,
                                        r.origin_id,
                                        p.id                              project_id,
                                        weight,
                                        r.target_id,
                                        -1 + row_number()
                                        OVER (PARTITION BY worker_id
                                          ORDER BY tw.created_at DESC) AS row_number

                                      FROM crowdsourcing_rating r
                                        INNER JOIN crowdsourcing_task t ON t.id = r.task_id
                                        INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                                        INNER JOIN crowdsourcing_taskworker tw ON t.id = tw.task_id
                                      WHERE origin_type = (%(origin_type)s)) t
                               GROUP BY origin_id, target_id, project_id)
                             m ON m.origin_id = p.owner_id AND p.id = m.project_id
                             AND m.target_id = mp.target_id
                             --AND m.task_w_avg < p.min_rating
              INNER JOIN (SELECT
                            group_id,
                            max(id) max_id
                          FROM crowdsourcing_project
                          WHERE status = (%(in_progress)s)
                          GROUP BY group_id) most_recent
                ON most_recent.max_id = p.id
            WHERE p.rating_updated_at < now() + ('4 second')::INTERVAL -
               ((%(HEART_BEAT_BOOMERANG)s) ||' minute')::INTERVAL AND p.min_rating > 0
            ) t WHERE t.avg_worker_rating < t.min_rating
            GROUP BY t.pid, t.name, t.min_rating, t.task_count, t.tasks_in_progress) combined
            )
        UPDATE crowdsourcing_project p
        SET min_rating = boomerang_ratings.new_min_rating, rating_updated_at = now(), tasks_in_progress = CASE WHEN
            boomerang_ratings.new_min_rating <> p.min_rating OR (boomerang_ratings.new_min_rating = p.min_rating AND
              boomerang_ratings.task_count > boomerang_ratings.tasks_in_progress)
            THEN boomerang_ratings.task_count ELSE
            boomerang_ratings.tasks_in_progress END
        FROM boomerang_ratings
        WHERE boomerang_ratings.pid = p.id
        RETURNING p.id, p.group_id, p.min_rating, p.rating_updated_at
    '''

    cursor.execute(query, {'in_progress': models.Project.STATUS_IN_PROGRESS,
                           'HEART_BEAT_BOOMERANG': settings.HEART_BEAT_BOOMERANG,
                           'BOOMERANG_TASK_ALPHA': settings.BOOMERANG_TASK_ALPHA,
                           'BOOMERANG_REQUESTER_ALPHA': settings.BOOMERANG_REQUESTER_ALPHA,
                           'BOOMERANG_PLATFORM_ALPHA': settings.BOOMERANG_PLATFORM_ALPHA,
                           'BOOMERANG_MIDPOINT': settings.BOOMERANG_MIDPOINT,
                           'BOOMERANG_LAMBDA': settings.BOOMERANG_LAMBDA,
                           'origin_type': models.Rating.RATING_REQUESTER})
    projects = cursor.fetchall()
    logs = []
    for project in projects:
        logs.append(models.BoomerangLog(project_id=project[1], min_rating=project[2], rating_updated_at=project[3],
                                        reason='DEFAULT'))
    models.BoomerangLog.objects.bulk_create(logs)

    return 'SUCCESS: {} rows affected'.format(cursor.rowcount)


@celery_app.task(ignore_result=True)
def update_project_boomerang(project_id):
    project = models.Project.objects.filter(pk=project_id).first()
    if project is not None and project.min_rating <= settings.BOOMERANG_MIDPOINT:
        rated_workers = models.Rating.objects.filter(origin=project.owner, origin_type=models.Rating.RATING_REQUESTER,
                                                     weight__gt=settings.BOOMERANG_MIDPOINT).count()
        if rated_workers > 0:
            project.min_rating = 3.0
            project.rating_updated_at = timezone.now()
            project.save()
            models.BoomerangLog.objects.create(project_id=project.group_id, min_rating=project.min_rating,
                                               rating_updated_at=project.rating_updated_at, reason='RESET')
    return 'SUCCESS'
