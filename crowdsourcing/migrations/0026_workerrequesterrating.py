# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0025_auto_20150805_1718'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkerRequesterRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.FloatField()),
                ('type', models.CharField(max_length=16)),
                ('origin', models.ForeignKey(related_name='rating_origin', to='crowdsourcing.UserProfile')),
                ('target', models.ForeignKey(related_name='rating_target', to='crowdsourcing.UserProfile')),
            ],
        ),
    ]
