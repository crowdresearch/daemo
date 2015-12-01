# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0064_auto_20151124_2003'),
    ]

    operations = [
        migrations.RenameField(
            model_name='module',
            old_name='module_timeout',
            new_name='timeout',
        ),
        migrations.AlterField(
            model_name='module',
            name='data_set_location',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=models.TextField(max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='name',
            field=models.CharField(default=b'Untitled Milestone', max_length=128, error_messages={b'required': b'Please enter the milestone name!'}),
        ),
        migrations.AlterField(
            model_name='module',
            name='price',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='task_time',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(default=b'Untitled Project', max_length=128, error_messages={b'required': b'Please enter the project name!'}),
        ),
    ]
