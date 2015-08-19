# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0031_auto_20150814_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerrequesterrating',
            name='created_timestamp',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 14, 20, 8, 53, 936528, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workerrequesterrating',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 14, 20, 9, 0, 336441, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workerrequesterrating',
            name='weight',
            field=models.IntegerField(default=2, choices=[(1, b'BelowExpectations'), (2, b'MetExpectations'), (3, b'ExceedsExpectations')]),
        ),
    ]
