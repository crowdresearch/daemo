# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0021_auto_20150728_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(error_messages={'required': 'Please specify the street name!'}, max_length=128),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(error_messages={'required': 'Please enter the category name!'}, max_length=128),
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(error_messages={'required': 'Please specify the city!'}, max_length=64),
        ),
        migrations.AlterField(
            model_name='country',
            name='code',
            field=models.CharField(error_messages={'required': 'Please specify the country code!'}, max_length=8),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(error_messages={'required': 'Please specify the country!'}, max_length=64),
        ),
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(error_messages={'required': 'Please specify the language!'}, max_length=64),
        ),
        migrations.AlterField(
            model_name='module',
            name='data_set_location',
            field=models.CharField(null=True, max_length=256, default='No data set'),
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=models.TextField(error_messages={'required': 'Please enter the module description!'}),
        ),
        migrations.AlterField(
            model_name='module',
            name='name',
            field=models.CharField(error_messages={'required': 'Please enter the module name!'}, max_length=128),
        ),
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Created'), (2, 'In Review'), (3, 'In Progress'), (4, 'Completed')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.CharField(max_length=1024, default=''),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(error_messages={'required': 'Please enter the project name!'}, max_length=128),
        ),
        migrations.AlterField(
            model_name='qualification',
            name='type',
            field=models.IntegerField(default=1, choices=[(1, 'Strict'), (2, 'Flexible')]),
        ),
        migrations.AlterField(
            model_name='region',
            name='code',
            field=models.CharField(error_messages={'required': 'Please specify the region code!'}, max_length=16),
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(error_messages={'required': 'Please specify the region!'}, max_length=64),
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(error_messages={'required': 'Please specify the role name!', 'unique': 'The role %(value)r already exists. Please provide another name!'}, max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name='skill',
            name='description',
            field=models.CharField(error_messages={'required': 'Please enter the skill description!'}, max_length=512),
        ),
        migrations.AlterField(
            model_name='skill',
            name='name',
            field=models.CharField(error_messages={'required': 'Please enter the skill name!'}, max_length=128),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Created'), (2, 'Accepted'), (3, 'Assigned'), (4, 'Finished')]),
        ),
        migrations.AlterField(
            model_name='taskworkerresult',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Created'), (2, 'Accepted'), (3, 'Rejected')]),
        ),
        migrations.AlterField(
            model_name='template',
            name='name',
            field=models.CharField(error_messages={'required': 'Please enter the template name!'}, max_length=128),
        ),
        migrations.AlterField(
            model_name='templateitem',
            name='layout',
            field=models.CharField(max_length=16, default='column'),
        ),
        migrations.AlterField(
            model_name='templateitem',
            name='name',
            field=models.CharField(error_messages={'required': 'Please enter the name of the template item!'}, max_length=128),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='birthday',
            field=models.DateField(null=True, error_messages={'invalid': 'Please enter a correct date format'}),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='requester_alias',
            field=models.CharField(error_messages={'required': 'Please enter an alias!'}, max_length=32),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='worker_alias',
            field=models.CharField(error_messages={'required': 'Please enter an alias!'}, max_length=32),
        ),
        migrations.AlterField(
            model_name='workermoduleapplication',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Created'), (2, 'Accepted'), (3, 'Rejected')]),
        ),
    ]
