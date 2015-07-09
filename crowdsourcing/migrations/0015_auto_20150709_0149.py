# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0014_auto_20150709_0139'),
    ]

    operations = [
        migrations.RenameField(
            model_name='conversation',
            old_name='created_by',
            new_name='sender',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='sent_from',
            new_name='sender',
        ),
        migrations.RenameField(
            model_name='messagerecipient',
            old_name='sent_to',
            new_name='recipient',
        ),
        migrations.AddField(
            model_name='conversation',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
