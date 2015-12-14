# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0071_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='template',
            field=models.ManyToManyField(to='crowdsourcing.Template', through='crowdsourcing.ModuleTemplate'),
        ),
    ]
