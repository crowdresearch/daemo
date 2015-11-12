# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0066_auto_20151111_0518'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialaccount',
            name='is_system',
            field=models.BooleanField(default=False),
        ),
    ]
