# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0055_auto_20150914_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='submodule',
            name='taskworkers',
            field=models.ManyToManyField(to='crowdsourcing.TaskWorker'),
        ),
    ]
