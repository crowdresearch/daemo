# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0005_auto_20150707_1244'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='has_multiple_tasks',
        ),
        migrations.AddField(
            model_name='module',
            name='data_set_location',
            field=models.CharField(default=b'No data set', max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='module',
            name='has_data_set',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='module',
            name='task_time',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='template',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='template',
            name='share_with_others',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='templateitem',
            name='data_source',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='templateitem',
            name='icon',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='templateitem',
            name='id_string',
            field=models.CharField(default='Label1', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='layout',
            field=models.CharField(default=b'column', max_length=16),
        ),
        migrations.AddField(
            model_name='templateitem',
            name='role',
            field=models.CharField(default='display', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='sub_type',
            field=models.CharField(default='h4', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='type',
            field=models.CharField(default='label', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='values',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='keywords',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='template',
            name='source_html',
            field=models.TextField(default=None, null=True),
        ),
    ]
