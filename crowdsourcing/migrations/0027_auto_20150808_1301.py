# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0026_workerrequesterrating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='requester_alias',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='worker_alias',
        ),
        migrations.AddField(
            model_name='requester',
            name='alias',
            field=models.CharField(default='none', max_length=32, error_messages={b'required': b'Please enter an alias!'}),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='worker',
            name='alias',
            field=models.CharField(default='none', max_length=32, error_messages={b'required': b'Please enter an alias!'}),
            preserve_default=False,
        ),
    ]
