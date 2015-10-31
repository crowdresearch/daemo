# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0053_auto_20150914_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='submodule',
            name='hours_before_results',
            field=models.IntegerField(default=1),
        ),
    ]
