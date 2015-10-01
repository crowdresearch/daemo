# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0046_requesterexperiment_taskranking_workerexperiment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskranking',
            name='task',
        ),
        migrations.RemoveField(
            model_name='taskranking',
            name='worker',
        ),
        migrations.RenameField(
            model_name='workerexperiment',
            old_name='requester',
            new_name='worker',
        ),
        migrations.DeleteModel(
            name='TaskRanking',
        ),
    ]
