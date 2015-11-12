# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0069_auto_20151111_2339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='id_string',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
