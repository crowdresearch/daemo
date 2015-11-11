# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0064_auto_20151111_0152'),
    ]

    operations = [
        migrations.AddField(
            model_name='paypalflow',
            name='created_timestamp',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 11, 2, 2, 39, 336000, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paypalflow',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 11, 2, 2, 45, 951886, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
