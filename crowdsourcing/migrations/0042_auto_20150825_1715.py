# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0041_auto_20150825_0240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='min_rating',
            field=models.FloatField(default=0),
        ),
    ]
