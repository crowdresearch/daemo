# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-07-19 10:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0188_taskworker_returned_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='post_id',
            field=models.IntegerField(default=-1, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='topic_id',
            field=models.IntegerField(default=-1, null=True),
        ),
    ]