# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0063_financialaccount_paypalflow_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='currency',
            field=models.CharField(default=b'USD', max_length=4),
        ),
    ]
