# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0038_module_min_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(max_length=8192)),
                ('deleted', models.BooleanField(default=False)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(related_name='reply_to', to='crowdsourcing.Feedback', null=True)),
                ('sender', models.ForeignKey(related_name='feedback_sender', to='crowdsourcing.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='ModuleFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('feedback', models.ForeignKey(related_name='feedback_feedback', to='crowdsourcing.Feedback')),
            ],
        ),
        migrations.AddField(
            model_name='module',
            name='allow_feedback',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='module',
            name='feedback_permissions',
            field=models.IntegerField(default=1, choices=[(1, b'Others:Read+Write::Workers:Read+Write'), (2, b'Others:Read::Workers:Read+Write'), (3, b'Others:Read::Workers:Read')]),
        ),
        migrations.AddField(
            model_name='modulefeedback',
            name='module',
            field=models.ForeignKey(related_name='feedback_module', to='crowdsourcing.Module'),
        ),
    ]
