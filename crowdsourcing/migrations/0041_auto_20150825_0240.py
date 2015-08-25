# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0040_auto_20150824_2013'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['created_timestamp']},
        ),
        migrations.RenameField(
            model_name='taskcomment',
            old_name='module',
            new_name='task',
        ),
        migrations.AlterField(
            model_name='module',
            name='feedback_permissions',
            field=models.IntegerField(default=1, choices=[(1, b'Others:Read+Write::Workers:Read+Write'), (2, b'Others:Read::Workers:Read+Write'), (3, b'Others:Read::Workers:Read'), (4, b'Others:None::Workers:Read')]),
        ),
        migrations.AlterField(
            model_name='taskworker',
            name='task_status',
            field=models.IntegerField(default=1, choices=[(1, b'In Progress'), (2, b'Submitted'), (3, b'Accepted'), (4, b'Rejected'), (5, b'Returned'), (6, b'Skipped')]),
        ),
    ]
