# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0019_conversationrecipient_date_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversationrecipient',
            name='conversation',
            field=models.ForeignKey(related_name='conversation_recipient', to='crowdsourcing.Conversation'),
        ),
        migrations.AlterField(
            model_name='message',
            name='conversation',
            field=models.ForeignKey(related_name='messages', to='crowdsourcing.Conversation'),
        ),
    ]
