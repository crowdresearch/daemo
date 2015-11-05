# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0059_auto_20150918_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modulepool',
            name='module',
        ),
        migrations.RemoveField(
            model_name='requesterexperiment',
            name='requester',
        ),
        migrations.RemoveField(
            model_name='submodule',
            name='fake_module',
        ),
        migrations.RemoveField(
            model_name='submodule',
            name='origin_module',
        ),
        migrations.RemoveField(
            model_name='submodule',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='workerexperiment',
            name='worker',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_active',
            field=models.DateTimeField(null=True),
        ),
        migrations.DeleteModel(
            name='ModulePool',
        ),
        migrations.DeleteModel(
            name='RequesterExperiment',
        ),
        migrations.DeleteModel(
            name='SubModule',
        ),
        migrations.DeleteModel(
            name='WorkerExperiment',
        ),
    ]
