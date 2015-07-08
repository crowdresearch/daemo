# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookmarkedProjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile', models.ForeignKey(to='crowdsourcing.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='ModuleTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='worker',
            name='alias',
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
            name='price',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='module',
            name='task_time',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='save_to_drive',
            field=models.BooleanField(default=False),
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
            field=models.CharField(default='adf', max_length=128),
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
            field=models.CharField(default='asdf', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='sub_type',
            field=models.CharField(default='asdf', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='templateitem',
            name='type',
            field=models.CharField(default='asdf', max_length=16),
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
            model_name='module',
            name='module_timeout',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='module',
            name='project',
            field=models.ForeignKey(related_name='modules', to='crowdsourcing.Project'),
        ),
        migrations.AlterField(
            model_name='module',
            name='repetition',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'In Review'), (3, b'In Progress'), (4, b'Completed')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='keywords',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='taskworkerresult',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'In Progress'), (2, b'Submitted'), (3, b'Approved'), (4, b'Rejected')]),
        ),
        migrations.AlterField(
            model_name='template',
            name='owner',
            field=models.ForeignKey(to='crowdsourcing.UserProfile'),
        ),
        migrations.AlterField(
            model_name='template',
            name='source_html',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='templateitem',
            name='template',
            field=models.ForeignKey(related_name='template_items', to='crowdsourcing.Template'),
        ),
        migrations.AddField(
            model_name='moduletemplate',
            name='module',
            field=models.ForeignKey(to='crowdsourcing.Module'),
        ),
        migrations.AddField(
            model_name='moduletemplate',
            name='template',
            field=models.ForeignKey(to='crowdsourcing.Template'),
        ),
        migrations.AddField(
            model_name='bookmarkedprojects',
            name='project',
            field=models.ForeignKey(to='crowdsourcing.Project'),
        ),
        migrations.AddField(
            model_name='module',
            name='template',
            field=models.ManyToManyField(to='crowdsourcing.Template', through='crowdsourcing.ModuleTemplate'),
        ),
    ]
