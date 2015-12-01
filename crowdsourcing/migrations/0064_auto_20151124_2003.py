# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0063_auto_20151119_2242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=3, choices=[(1, b'Draft'), (2, b'Saved'), (3, b'Published'), (4, b'Completed'), (5, b'Paused')]),
        ),
    ]
