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
from crowdsourcing.models import TaskWorker, PayPalPayoutLog
from crowdsourcing.redis import RedisProvider
from crowdsourcing.utils import PayPalBackend
from csp.celery import app as celery_app


@celery_app.task
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
                WHERE p.timeout IS NOT NULL AND tw.created_at + p.timeout * INTERVAL '1 minute' < NOW()
                AND tw.status=%(in_progress)s)
                UPDATE crowdsourcing_taskworker tw_up SET status=%(expired)s
            FROM taskworkers
            WHERE taskworkers.id=tw_up.id
            RETURNING tw_up.id, tw_up.worker_id
        '''
    cursor.execute(query, {'in_progress': TaskWorker.STATUS_IN_PROGRESS, 'expired': TaskWorker.STATUS_EXPIRED})
    workers = cursor.fetchall()
    worker_list = []
    task_workers = []
    for w in workers:
        worker_list.append(w[1])
        task_workers.append({'id': w[0]})
    refund_task.delay(task_workers)
    update_worker_cache.delay(worker_list, constants.TASK_EXPIRED)
    return 'SUCCESS'


@celery_app.task
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


@celery_app.task
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


@celery_app.task(bind=True)
def create_tasks(self, tasks):
    try:
        with transaction.atomic():
            task_obj = []
            x = 0
            for task in tasks:
                x += 1
                t = models.Task(data=task['data'], project_id=task['project_id'],
                                row_number=x)
                task_obj.append(t)
            models.Task.objects.bulk_create(task_obj)
            models.Task.objects.filter(project_id=tasks[0]['project_id']).update(group_id=F('id'))
    except Exception as e:
        self.retry(countdown=4, exc=e, max_retries=2)

    return 'SUCCESS'


@celery_app.task(bind=True)
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
                t = models.Task(data=row, project_id=int(project_id), row_number=x)
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


@celery_app.task
def pay_workers():
    workers = User.objects.all()
    total = 0

    for worker in workers:
        tasks = TaskWorker.objects.values('task__project__price', 'id').filter(worker=worker,
                                                                               status=TaskWorker.STATUS_ACCEPTED,
                                                                               is_paid=False)
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
    payout_log = PayPalPayoutLog()
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


@celery_app.task
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


@celery_app.task
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
