# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0058_workerexperiment_feedback_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerexperiment',
            name='feedback_required',
            field=models.BooleanField(default=False),
        ),
    ]
