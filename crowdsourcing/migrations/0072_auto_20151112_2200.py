# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0071_auto_20151112_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialaccount',
            name='owner',
            field=models.ForeignKey(related_name='account_owner', to='crowdsourcing.UserProfile', null=True),
        ),
    ]
