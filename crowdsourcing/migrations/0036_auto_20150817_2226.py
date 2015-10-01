# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0035_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerrequesterrating',
            name='weight',
            field=models.FloatField(default=2),
        ),
    ]
