# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0025_auto_20150805_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskworker',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'In Progress'), (3, b'Submitted'), (4, b'Accepted'), (5, b'Returned')]),
        ),
    ]
