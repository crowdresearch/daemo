# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0039_auto_20150824_2009'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(max_length=8192)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(related_name='reply_to', to='crowdsourcing.Comment', null=True)),
                ('sender', models.ForeignKey(related_name='comment_sender', to='crowdsourcing.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='ModuleComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(related_name='modulecomment_comment', to='crowdsourcing.Comment')),
                ('module', models.ForeignKey(related_name='modulecomment_module', to='crowdsourcing.Module')),
            ],
        ),
        migrations.CreateModel(
            name='TaskComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(related_name='taskcomment_comment', to='crowdsourcing.Comment')),
                ('module', models.ForeignKey(related_name='taskcomment_task', to='crowdsourcing.Task')),
            ],
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='modulefeedback',
            name='feedback',
        ),
        migrations.RemoveField(
            model_name='modulefeedback',
            name='module',
        ),
        migrations.DeleteModel(
            name='Feedback',
        ),
        migrations.DeleteModel(
            name='ModuleFeedback',
        ),
    ]
