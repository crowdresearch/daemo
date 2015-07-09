# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crowdsourcing', '0016_auto_20150709_0201'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='recipients',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='crowdsourcing.ConversationRecipient'),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='sender',
            field=models.ForeignKey(related_name='sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='conversationrecipient',
            name='message',
            field=models.ForeignKey(related_name='conversation_message', to='crowdsourcing.Conversation'),
        ),
        migrations.AlterField(
            model_name='conversationrecipient',
            name='recipient',
            field=models.ForeignKey(related_name='recipients', to=settings.AUTH_USER_MODEL),
        ),
    ]
