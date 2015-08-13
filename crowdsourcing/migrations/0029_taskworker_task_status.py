# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0028_module_is_micro'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskworker',
            name='task_status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'Accepted'), (3, b'Rejected'), (4, b'Returned'), (5, b'Skipped')]),
        ),
    ]
