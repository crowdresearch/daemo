# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0030_module_is_prototype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskworker',
            name='task_status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'In Progress'), (3, b'Accepted'), (4, b'Rejected'), (5, b'Returned'), (6, b'Skipped')]),
        ),
    ]
