# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0061_auto_20151019_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_active',
            field=models.DateTimeField(null=True),
        ),
    ]
