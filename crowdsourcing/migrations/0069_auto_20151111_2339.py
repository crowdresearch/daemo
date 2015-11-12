# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0068_auto_20151111_2337'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paypalflow',
            name='token',
        ),
        migrations.AddField(
            model_name='paypalflow',
            name='redirect_url',
            field=models.CharField(default='https://', max_length=256),
            preserve_default=False,
        ),
    ]
