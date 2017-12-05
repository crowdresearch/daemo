from __future__ import division

import json
from collections import OrderedDict
from datetime import timedelta
from decimal import Decimal, ROUND_UP

import numpy as np
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection, transaction
from django.db.models import F, Q
from django.utils import timezone
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

import constants
from crowdsourcing import models
from crowdsourcing.crypto import to_hash
from crowdsourcing.emails import send_notifications_email, send_new_tasks_email, send_task_returned_email, \
    send_task_rejected_email, send_project_completed
from crowdsourcing.payment import Stripe
from crowdsourcing.redis import RedisProvider
from crowdsourcing.utils import hash_task
from csp.celery import app as celery_app
from mturk.tasks import get_provider


def _expire_returned_tasks():
    now = timezone.now()
    if now.weekday() in [5, 6]:
        return 'WEEKEND'
    # noinspection SqlResolve
    query = '''
        with task_workers as (
            SELECT *
            FROM (
                   SELECT
                     tw.id,
                     CASE WHEN EXTRACT(DOW FROM now()) <= %(dow)s
                       THEN tw.returned_at + INTERVAL %(exp_days)s
                     ELSE tw.returned_at END returned_at
                   FROM crowdsourcing_taskworker tw
                     INNER JOIN crowdsourcing_task t ON tw.task_id = t.id
                   WHERE tw.status = %(status)s) r
            WHERE (now() - INTERVAL %(exp_days)s)::timestamp > r.returned_at
        )
        UPDATE crowdsourcing_taskworker tw_up SET status=%(expired)s, updated_at=now()
            FROM task_workers
            WHERE task_workers.id=tw_up.id
            RETURNING tw_up.id, tw_up.worker_id

    '''
    cursor = connection.cursor()
    cursor.execute(query,
                   {
                       'status': models.TaskWorker.STATUS_RETURNED,
                       'expired': models.TaskWorker.STATUS_EXPIRED,
                       'exp_days': '{} day'.format(settings.EXPIRE_RETURNED_TASKS),
                       'dow': settings.EXPIRE_RETURNED_TASKS
                   })

    workers = cursor.fetchall()
    cursor.close()
    worker_list = []
    task_workers = []
    for w in workers:
        worker_list.append(w[1])
        task_workers.append({'id': w[0]})
    refund_task.delay(task_workers)
    update_worker_cache.delay(worker_list, constants.TASK_EXPIRED)
    return 'SUCCESS'


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
                INNER JOIN crowdsourcing_taskworkersession sessions ON sessions.task_worker_id = tw.id
                WHERE tw.status=%(in_progress)s
                GROUP BY tw.id, p.id
                HAVING sum(coalesce(sessions.ended_at, now()) - sessions.started_at) >
                    coalesce(p.timeout, INTERVAL '24 hour'))
                UPDATE crowdsourcing_taskworker tw_up SET status=%(expired)s
            FROM taskworkers
            WHERE taskworkers.id=tw_up.id
            RETURNING tw_up.id, tw_up.worker_id
        '''
    cursor.execute(query,
                   {'in_progress': models.TaskWorker.STATUS_IN_PROGRESS, 'expired': models.TaskWorker.STATUS_EXPIRED})
    workers = cursor.fetchall()
    cursor.close()
    worker_list = []
    task_workers = []
    for w in workers:
        worker_list.append(w[1])
        task_workers.append({'id': w[0]})
    refund_task.delay(task_workers)
    update_worker_cache.delay(worker_list, constants.TASK_EXPIRED)
    _expire_returned_tasks()

    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def auto_approve_tasks():
    now = timezone.now()
    # if now.weekday() in [5, 6]:
    #     return 'WEEKEND'
    # if now.weekday() == 0 and now.hour < 15:
    #     return 'MONDAY'
    cursor = connection.cursor()

    # noinspection SqlResolve
    query = '''
        WITH taskworkers AS (
            SELECT
              tw.id,
              p.id project_id,
              p.group_id project_gid,
              tw.task_id,
              u.id user_id,
              u.username,
              u_worker.username worker_username
            FROM crowdsourcing_taskworker tw
            INNER JOIN crowdsourcing_task t ON  tw.task_id = t.id
            INNER JOIN crowdsourcing_project p ON t.project_id = p.id
            INNER JOIN auth_user u ON p.owner_id = u.id
            INNER JOIN auth_user u_worker ON tw.worker_id = u_worker.id
            WHERE tw.submitted_at + INTERVAL %(auto_approve_freq)s < NOW()
            AND tw.status=%(submitted)s)
            UPDATE crowdsourcing_taskworker tw_up SET status=%(accepted)s, approved_at = %(approved_at)s,
            auto_approved=TRUE
        FROM taskworkers
        WHERE taskworkers.id=tw_up.id
        RETURNING tw_up.id, tw_up.worker_id, taskworkers.task_id, taskworkers.user_id, taskworkers.username,
        taskworkers.project_gid, taskworkers.worker_username
    '''
    cursor.execute(query,
                   {'submitted': models.TaskWorker.STATUS_SUBMITTED,
                    'accepted': models.TaskWorker.STATUS_ACCEPTED,
                    'approved_at': now,
                    'auto_approve_freq': '{} hour'.format(settings.AUTO_APPROVE_FREQ)})
    task_workers = cursor.fetchall()
    for w in task_workers:
        task_workers.append({'id': w[0]})
        post_approve.delay(w[2], 1)
        redis_publisher = RedisPublisher(facility='notifications', users=[w[4], w[6]])
        message = RedisMessage(
            json.dumps({"event": 'TASK_APPROVED', "project_gid": w[5], "project_key": to_hash(w[5])}))
        redis_publisher.publish_message(message)
    cursor.close()
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
        elif operation == constants.ACTION_GROUP_ADD:
            provider.set_add(name + ':worker_groups', value)
        elif operation == constants.ACTION_GROUP_REMOVE:
            provider.set_remove(name + ':worker_groups', value)
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
        if previous_batch_file is None and previous_rev is not None:
            task.group_id = previous_rev.tasks.all().first().group_id
        else:
            task.group_id = task.id
        task.save()
        # price_data = models.Task.objects.filter(project_id=project_id, price__isnull=False).values_list('price',
        #                                                                                                 flat=True)
        _set_aux_attributes(project, [])
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
                price = None
                if project.allow_price_per_task and project.task_price_field is not None:
                    price = row.get(project.task_price_field)
                t = models.Task(data=row, hash=hash_digest, project_id=int(project_id), row_number=x, price=price)
                if previous_batch_file is not None and x <= previous_count:
                    if len(set(row.items()) ^ set(previous_tasks[x - 1].data.items())) == 0:
                        t.group_id = previous_tasks[x - 1].group_id
                task_obj.append(t)
            models.Task.objects.bulk_create(task_obj)
            price_data = models.Task.objects.filter(project_id=project_id, price__isnull=False).values_list('price',
                                                                                                            flat=True)
            _set_aux_attributes(project, price_data)
            models.Task.objects.filter(project_id=project_id, group_id__isnull=True) \
                .update(group_id=F('id'))
    except Exception as e:
        self.retry(countdown=4, exc=e, max_retries=2)

    return 'SUCCESS'


def _set_aux_attributes(project, price_data):
    if project.aux_attributes is None:
        project.aux_attributes = {}
    if not len(price_data):
        max_price = float(project.price)
        min_price = float(project.price)
        median_price = float(project.price)
    else:
        max_price = float(np.max(price_data))
        min_price = float(np.min(price_data))
        median_price = float(np.median(price_data))
    project.aux_attributes.update({"min_price": min_price, "max_price": max_price, "median_price": median_price})
    project.save()


@celery_app.task(ignore_result=True)
def pay_workers():
    workers = User.objects.all()
    payment = Stripe()
    # total = 0
    #
    for worker in workers:
        task_workers = models.TaskWorker.objects.prefetch_related('task__project') \
            .filter(worker=worker,
                    status=models.TaskWorker.STATUS_ACCEPTED,
                    is_paid=False)
        for tw in task_workers:
            payment.pay_worker(tw)


def single_payout(amount, user):
    return 'OBSOLETE METHOD'


@celery_app.task(ignore_result=True)
def post_approve(task_id, num_workers):
    task = models.Task.objects.prefetch_related('project').get(pk=task_id)
    latest_revision = models.Project.objects.filter(~Q(status=models.Project.STATUS_DRAFT),
                                                    group_id=task.project.group_id) \
        .order_by('-id').first()
    latest_revision.amount_due -= Decimal(num_workers * latest_revision.price)
    latest_revision.save()
    return 'SUCCESS'


def create_transaction(sender_id, recipient_id, amount, reference):
    return 'OBSOLETE METHOD'


@celery_app.task(ignore_result=True)
def refund_task(task_worker_in):
    return 'OBSOLETE METHOD'


@celery_app.task(ignore_result=True)
def update_feed_boomerang():
    logs = []
    cursor = connection.cursor()
    last_update = timezone.now() - timedelta(minutes=settings.HEART_BEAT_BOOMERANG)
    projects = models.Project.objects.filter(status=models.Project.STATUS_IN_PROGRESS,
                                             min_rating__gt=1.0,
                                             enable_boomerang=True,
                                             rating_updated_at__lt=last_update)
    for project in projects:
        if project.min_rating == 3.0:
            project.min_rating = 2.0
            project.previous_min_rating = 3.0
        elif project.min_rating == 2.0:
            project.min_rating = 1.99
            project.previous_min_rating = 2.0
        elif project.min_rating == 1.99:
            project.min_rating = 1.0
            project.previous_min_rating = 1.99
        project.rating_updated_at = timezone.now()
        project.save()
        logs.append(
            models.BoomerangLog(object_id=project.group_id, min_rating=project.min_rating,
                                rating_updated_at=project.rating_updated_at,
                                reason='DEFAULT'))
    # noinspection SqlResolve
    email_query = '''
        SELECT
          available.id,
          available.group_id,
          owner_profile.handle,
          u_workers.id,
          sum(available) available_count,
          u_workers.email,
          available.name,
          coalesce((available.aux_attributes ->> 'median_price') :: NUMERIC, available.price)
        FROM (
               SELECT
                 p.id,
                 p.group_id,
                 p.name,
                 owner_id,
                 p.min_rating,
                 p.price,
                 p.aux_attributes,
                 sum(1) available
               FROM crowdsourcing_task t
                 INNER JOIN (SELECT
                               group_id,
                               max(id) id
                             FROM crowdsourcing_task
                             WHERE deleted_at IS NULL
                             GROUP BY group_id) t_max ON t_max.id = t.id
                 INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                 INNER JOIN (
                              SELECT
                                t.group_id,
                                sum(t.done) done
                              FROM (
                                     SELECT
                                       t.group_id,
                                       CASE WHEN (tw.worker_id IS NOT NULL)
                                                 AND tw.status NOT IN (4, 6, 7)
                                         THEN 1
                                       ELSE 0 END done
                                     FROM crowdsourcing_task t
                                       LEFT OUTER JOIN crowdsourcing_taskworker tw ON t.id = tw.task_id
                                     WHERE t.exclude_at IS NULL AND t.deleted_at IS NULL) t
                              GROUP BY t.group_id)
                            t_count ON t_count.group_id = t.group_id AND t_count.done < p.repetition
               WHERE p.status = 3 AND p.deleted_at IS NULL
               GROUP BY p.id, p.name, owner_id, p.min_rating, p.group_id, p.price, aux_attributes) available
          INNER JOIN auth_user u_workers ON TRUE
          INNER JOIN crowdsourcing_userprofile p_workers ON p_workers.user_id = u_workers.id
          AND p_workers.is_worker IS TRUE
          INNER JOIN get_worker_ratings(u_workers.id) worker_ratings
            ON worker_ratings.requester_id = available.owner_id
               AND (coalesce(worker_ratings.worker_rating, 1.99) >= available.min_rating)
          LEFT OUTER JOIN crowdsourcing_WorkerProjectNotification n
            ON n.project_id = available.group_id AND n.worker_id = u_workers.id
          INNER JOIN crowdsourcing_userpreferences pref ON pref.user_id = u_workers.id
          INNER JOIN auth_user owner ON owner.id = available.owner_id
          INNER JOIN crowdsourcing_userprofile owner_profile ON owner_profile.user_id = owner.id
          LEFT OUTER JOIN (
                            SELECT
                              p.id,
                              tw.worker_id,
                              count(tw.id) tasks_done
                            FROM crowdsourcing_project p
                              INNER JOIN crowdsourcing_task t ON p.id = t.project_id
                              LEFT OUTER JOIN crowdsourcing_taskworker tw ON tw.task_id = t.id
                            GROUP BY p.id, tw.worker_id
                          ) worker_project ON worker_project.id = available.id
                           AND worker_project.worker_id = u_workers.id
        WHERE n.id IS NULL AND pref.new_tasks_notifications = TRUE AND coalesce(worker_project.tasks_done, 0) = 0
        GROUP BY available.id, available.group_id, owner_profile.handle, u_workers.id, u_workers.email, available.name,
          available.price, available.aux_attributes;
    '''

    try:
        cursor.execute(email_query, {})
        workers = cursor.fetchall()
        worker_project_notifications = []
        for worker in workers:
            try:
                send_new_tasks_email(to=worker[5], project_id=worker[0],
                                     project_name=worker[6], price=worker[7],
                                     available_tasks=worker[4], requester_handle=worker[2])
                worker_project_notifications.append(models.WorkerProjectNotification(project_id=worker[1],
                                                                                     worker_id=worker[3]))
            except Exception as e:
                print(e)
        models.WorkerProjectNotification.objects.bulk_create(worker_project_notifications)
    except Exception as e:
        print(e)
    cursor.close()

    # for task in tasks:
    #     logs.append(models.BoomerangLog(object_id=task[1], min_rating=task[2], object_type='task',
    #                                     rating_updated_at=task[3],
    #                                     reason='DEFAULT'))

    models.BoomerangLog.objects.bulk_create(logs)

    return 'SUCCESS: {} rows affected'.format(cursor.rowcount)


@celery_app.task(ignore_result=True)
def update_project_boomerang(project_id):
    project = models.Project.objects.filter(pk=project_id).first()
    if project is not None:
        project.min_rating = 3.0
        # project.rating_updated_at = timezone.now()
        project.save()
        models.BoomerangLog.objects.create(object_id=project.group_id, min_rating=project.min_rating,
                                           rating_updated_at=project.rating_updated_at, reason='RESET')
    return 'SUCCESS'


@celery_app.task
def background_task(function, **kwargs):
    function(**kwargs)
    return 'SUCCESS'


# Payment Tasks
@celery_app.task(ignore_result=True)
def create_account_and_customer(user_id, ip_address):
    from crowdsourcing.payment import Stripe
    try:
        user = User.objects.get(pk=user_id)
        Stripe().create_account_and_customer(user=user, country_iso=user.profile.address.city.country.code,
                                             ip_address=ip_address)
    except User.DoesNotExist:
        return 'User does not exist'
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def refund_charges_before_expiration():
    from crowdsourcing.payment import Stripe
    charges = models.StripeCharge.objects.filter(expired=False, balance__gt=50,
                                                 created_at__gt=timezone.now() - settings.STRIPE_CHARGE_LIFETIME)

    for charge in charges:
        try:
            Stripe().refund(charge=charge, amount=charge.balance)
            charge.expired = True
            charge.expired_at = timezone.now()
            charge.save()
        except Exception:
            pass


@celery_app.task(ignore_result=True)
def notify_workers(project_id, worker_ids, subject, message):
    project = models.Project.objects.values('owner').get(id=project_id)

    user = User.objects.get(id=project['owner'])
    provider = get_provider(user)

    if provider is None:
        return

    provider.notify_workers(worker_ids=worker_ids, subject=subject, message_text=message)
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def send_return_notification_email(return_feedback_id, reject=False):
    feedback = models.ReturnFeedback.objects.prefetch_related('task_worker', 'task_worker__worker',
                                                              'task_worker__task__project',
                                                              'task_worker__task__project__owner__profile').get(
        id=return_feedback_id)
    if not feedback.notification_sent:
        if not reject:
            send_task_returned_email(to=feedback.task_worker.worker.email,
                                     requester_handle=feedback.task_worker.task.project.owner.profile.handle,
                                     project_name=feedback.task_worker.task.project.name[:32],
                                     task_id=feedback.task_worker.task_id,
                                     return_reason=feedback.body,
                                     requester_email=feedback.task_worker.task.project.owner.email)
        else:
            send_task_rejected_email(to=feedback.task_worker.worker.email,
                                     requester_handle=feedback.task_worker.task.project.owner.profile.handle,
                                     project_name=feedback.task_worker.task.project.name[:32],
                                     task_id=feedback.task_worker.task_id,
                                     reject_reason=feedback.body,
                                     requester_email=feedback.task_worker.task.project.owner.email)
        feedback.notification_sent = True
        feedback.notification_sent_at = timezone.now()
        feedback.save()


@celery_app.task(ignore_result=True)
def check_project_completed(project_id):
    query = '''
         SELECT
              count(t.id) remaining

            FROM crowdsourcing_task t INNER JOIN (SELECT
                                                    group_id,
                                                    max(id) id
                                                  FROM crowdsourcing_task
                                                  WHERE deleted_at IS NULL
                                                  GROUP BY group_id) t_max ON t_max.id = t.id
              INNER JOIN crowdsourcing_project p ON p.id = t.project_id
              INNER JOIN (
                           SELECT
                             t.group_id,
                             sum(t.others) OTHERS
                           FROM (
                                  SELECT
                                    t.group_id,
                                    CASE WHEN tw.id IS NOT NULL THEN 1 ELSE 0 END OTHERS
                                  FROM crowdsourcing_task t
                                    LEFT OUTER JOIN crowdsourcing_taskworker tw
                                    ON (t.id = tw.task_id AND tw.status NOT IN (4, 6, 7))
                                  WHERE t.exclude_at IS NULL AND t.deleted_at IS NULL) t
                           GROUP BY t.group_id) t_count ON t_count.group_id = t.group_id
            WHERE t_count.others < p.repetition AND p.id=(%(project_id)s)
            GROUP BY p.id;
    '''
    params = {
        "project_id": project_id
    }
    cursor = connection.cursor()
    cursor.execute(query, params)
    remaining_count = cursor.fetchall()[0][0] if cursor.rowcount > 0 else 0
    print(remaining_count)
    if remaining_count == 0:
        with transaction.atomic():
            project = models.Project.objects.select_for_update().get(id=project_id)
            if project.is_prototype:
                feedback = project.comments.all()
                if feedback.count() > 0 and feedback.filter(ready_for_launch=True).count() / feedback.count() < 0.66:
                    # mandatory stop
                    pass
                else:
                    from crowdsourcing.serializers.project import ProjectSerializer
                    from crowdsourcing.viewsets.project import ProjectViewSet

                    needs_workers = project.repetition < project.aux_attributes.get('repetition', project.repetition)
                    needs_tasks = project.tasks.filter(exclude_at__isnull=True).count < project.aux_attributes.get(
                        'number_of_tasks')
                    if needs_workers or needs_tasks:
                        serializer = ProjectSerializer()
                        revision = ProjectSerializer.create_revision(project)
                        revision.repetition = revision.aux_attributes.get('repetition', project.repetition)
                        revision.is_prototype = False
                        revision.save()
                        serializer.create_tasks(revision.id, False)
                        total_needed = ProjectViewSet.calculate_total(revision)
                        to_pay = (Decimal(total_needed) - revision.amount_due).quantize(Decimal('.01'),
                                                                                        rounding=ROUND_UP)
                        revision.amount_due = total_needed if total_needed is not None else 0
                        if to_pay * 100 > revision.owner.stripe_customer.account_balance:
                            return 'FAILED'
                        else:
                            serializer = ProjectSerializer(instance=revision, data={})
                            if serializer.is_valid():
                                serializer.publish(to_pay)
                            return 'SUCCESS'

            else:
                send_project_completed(to=project.owner.email, project_name=project.name, project_id=project_id)
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def post_to_discourse(project_id):
    from crowdsourcing.discourse import DiscourseClient
    instance = models.Project.objects.get(id=project_id)
    aux_attrib = instance.aux_attributes

    if 'median_price' in aux_attrib:
        price = aux_attrib['median_price']

        if price is not None and float(price) > 0:
            price = float(price)
        else:
            price = instance.price
    else:
        price = instance.price

    # post topic as system user
    client = DiscourseClient(
        settings.DISCOURSE_BASE_URL,
        api_username='system',
        api_key=settings.DISCOURSE_API_KEY)

    if instance.discussion_link is None:

        try:
            topic = client.create_topic(title=instance.name,
                                        category=settings.DISCOURSE_TOPIC_TASKS,
                                        timeout=instance.timeout,
                                        price=price,
                                        requester_handle=instance.owner.profile.handle,
                                        project_id=project_id)

            if topic is not None:
                url = '/t/%s/%d' % (topic['topic_slug'], topic['topic_id'])
                instance.discussion_link = url
                instance.topic_id = topic['topic_id']
                instance.post_id = topic['id']
                instance.save()

            # watch as requester
            client = DiscourseClient(
                settings.DISCOURSE_BASE_URL,
                api_username=instance.owner.profile.handle,
                api_key=settings.DISCOURSE_API_KEY)

            client.watch_topic(topic_id=topic['topic_id'])

        except Exception as e:
            print(e)
            print 'failed to create or watch topic'

    else:
        # handle if any details changed and update first post again
        if instance.topic_id > 0 and instance.post_id > 0:
            preview_url = "%s/task-feed/%d" % (settings.SITE_HOST, project_id)
            content = "**Title**: [%s](%s) \n" \
                      "**Requester**: @%s\n" \
                      "**Price** : USD %.2f \n" \
                      "**Timeout** : %s \n" % (instance.name, preview_url, instance.owner.profile.handle, price,
                                               instance.timeout)

            try:
                client.update_post(
                    post_id=instance.post_id,
                    edit_reason='updating project parameters',
                    content=content)
            except Exception as e:
                print(e)
                print 'failed to update post'
