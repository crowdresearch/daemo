# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0069_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Draft'), (2, b'Saved'), (3, b'Published'), (4, b'Completed'), (5, b'Paused')]),
        ),
    ]
