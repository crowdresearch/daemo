# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0057_auto_20150914_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerexperiment',
            name='feedback_required',
            field=models.BooleanField(default=True),
        ),
    ]
