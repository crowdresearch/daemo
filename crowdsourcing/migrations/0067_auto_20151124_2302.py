# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0066_auto_20151124_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='keywords',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='task_time',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
