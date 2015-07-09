# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0017_auto_20150709_0204'),
    ]

    operations = [
        migrations.RenameField(
            model_name='conversationrecipient',
            old_name='message',
            new_name='conversation',
        ),
        migrations.RemoveField(
            model_name='conversationrecipient',
            name='status',
        ),
        migrations.AddField(
            model_name='message',
            name='status',
            field=models.IntegerField(default=1),
        ),
    ]
