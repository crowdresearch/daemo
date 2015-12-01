# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0065_auto_20151124_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='data_set_location',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=models.TextField(max_length=2048, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='price',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.CharField(max_length=1024, null=True, blank=True),
        ),
    ]
