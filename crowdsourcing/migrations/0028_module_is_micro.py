# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0027_auto_20150808_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='is_micro',
            field=models.BooleanField(default=True),
        ),
    ]
