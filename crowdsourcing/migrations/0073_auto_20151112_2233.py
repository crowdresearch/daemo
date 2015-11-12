# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0072_auto_20151112_2200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paypalflow',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='action',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='method',
            field=models.CharField(default=b'paypal', max_length=16),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sender_type',
            field=models.CharField(default=b'self', max_length=8),
        ),
    ]
