# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0029_taskworker_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='is_prototype',
            field=models.BooleanField(default=False),
        ),
    ]
