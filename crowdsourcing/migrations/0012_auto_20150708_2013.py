# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0011_auto_20150708_1151'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='data',
        ),
        migrations.AlterField(
            model_name='task',
            name='module',
            field=models.ForeignKey(related_name='tasks', to='crowdsourcing.Module'),
        ),
        migrations.AlterField(
            model_name='taskworker',
            name='task',
            field=models.ForeignKey(related_name='taskworkers', to='crowdsourcing.Task'),
        ),
        migrations.AlterField(
            model_name='taskworkerresult',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'In Progress'), (2, b'Submitted'), (3, b'Approved'), (4, b'Rejected')]),
        ),
        migrations.AlterField(
            model_name='taskworkerresult',
            name='task_worker',
            field=models.ForeignKey(related_name='taskworkerresults', to='crowdsourcing.TaskWorker'),
        ),
    ]
