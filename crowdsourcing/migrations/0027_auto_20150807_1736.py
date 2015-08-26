# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0026_taskworker_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskworker',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'In Progress'), (2, b'Submitted'), (3, b'Accepted'), (4, b'Returned')]),
        ),
    ]
