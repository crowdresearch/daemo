# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0037_auto_20150818_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='min_rating',
            field=models.FloatField(default=3.3),
        ),
    ]
