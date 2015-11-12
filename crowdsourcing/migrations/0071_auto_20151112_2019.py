# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0070_auto_20151112_2001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialaccount',
            name='id_string',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='id_string',
        ),
    ]
