# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0065_auto_20151111_0202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialaccount',
            name='profile',
        ),
        migrations.AddField(
            model_name='financialaccount',
            name='owner',
            field=models.ForeignKey(related_name='account_owner', default=1, to='crowdsourcing.UserProfile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='action',
            field=models.CharField(default='1', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
