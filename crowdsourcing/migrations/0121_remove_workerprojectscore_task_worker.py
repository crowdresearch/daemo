# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-29 22:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0120_workerprojectscore_task_worker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workerprojectscore',
            name='task_worker',
        ),
    ]