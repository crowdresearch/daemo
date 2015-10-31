# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0049_auto_20150914_0436'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubModule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('round', models.IntegerField(default=1)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
                ('owner', models.ForeignKey(to='crowdsourcing.RequesterExperiment')),
            ],
        ),
    ]
