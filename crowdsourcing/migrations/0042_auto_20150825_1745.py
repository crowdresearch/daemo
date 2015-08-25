# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0041_auto_20150825_0240'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskworker',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='module',
            name='min_rating',
            field=models.FloatField(default=0),
        ),
    ]
