# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0045_auto_20150901_0120'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequesterExperiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_prototype', models.BooleanField(default=True)),
                ('has_boomerang', models.BooleanField(default=True)),
                ('pool', models.IntegerField(default=0)),
                ('requester', models.ForeignKey(related_name='requester_experiment', to='crowdsourcing.Requester')),
            ],
        ),
        migrations.CreateModel(
            name='TaskRanking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.FloatField(default=0)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('task', models.ForeignKey(related_name='task_rating', to='crowdsourcing.Task')),
                ('worker', models.ForeignKey(related_name='task_rating_worker', to='crowdsourcing.Worker')),
            ],
        ),
        migrations.CreateModel(
            name='WorkerExperiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_prototype', models.BooleanField(default=True)),
                ('sorting_type', models.IntegerField(default=1)),
                ('is_subject_to_cascade', models.BooleanField(default=True)),
                ('pool', models.IntegerField(default=0)),
                ('requester', models.ForeignKey(related_name='worker_experiment', to='crowdsourcing.Worker')),
            ],
        ),
    ]
