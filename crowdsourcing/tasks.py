from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from django.utils import timezone

from crowdsourcing import models
from crowdsourcing.emails import send_notifications_email
from crowdsourcing.models import TaskWorker
from csp.celery import app as celery_app


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
        '''
    cursor.execute(query, {'in_progress': TaskWorker.STATUS_IN_PROGRESS, 'expired': TaskWorker.STATUS_EXPIRED})
    return 'SUCCESS'


@celery_app.task
def email_notifications():
    users = User.objects.all()

    url = '%s/%s' % (settings.SITE_HOST, 'messages')

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

            # update Email Notification for user - updated_at
            models.EmailNotification.objects.filter(recipient=user).update(updated_at=timezone.now())

    return 'SUCCESS'
