# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0056_submodule_taskworkers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submodule',
            name='taskworkers',
        ),
        migrations.AddField(
            model_name='submodule',
            name='taskworkers',
            field=django.contrib.postgres.fields.ArrayField(default=[], base_field=models.IntegerField(), size=None),
        ),
    ]
