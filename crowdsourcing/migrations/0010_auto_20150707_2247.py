# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0009_auto_20150707_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookmarkedProjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile', models.ForeignKey(to='crowdsourcing.UserProfile')),
                ('project', models.ForeignKey(to='crowdsourcing.Project')),
            ],
        ),
        migrations.AddField(
            model_name='module',
            name='template',
            field=models.ManyToManyField(to='crowdsourcing.Template', through='crowdsourcing.ModuleTemplate'),
        ),
    ]
