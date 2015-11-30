# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='is_deleted',
        ),
        migrations.AlterField(
            model_name='financialaccount',
            name='balance',
            field=models.DecimalField(default=0, max_digits=19, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='financialaccount',
            name='owner',
            field=models.ForeignKey(related_name='financial_accounts', to='crowdsourcing.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(max_digits=19, decimal_places=4),
        ),
    ]
