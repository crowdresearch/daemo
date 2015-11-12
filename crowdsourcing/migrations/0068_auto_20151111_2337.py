# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0067_financialaccount_is_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='paypalflow',
            name='payer_id',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='paypalflow',
            name='token',
            field=models.CharField(default='EC-7CSZ23', max_length=64),
            preserve_default=False,
        ),
    ]
