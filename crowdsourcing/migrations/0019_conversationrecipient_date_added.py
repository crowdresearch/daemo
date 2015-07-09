# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0018_auto_20150709_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversationrecipient',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 9, 2, 17, 3, 587241, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
