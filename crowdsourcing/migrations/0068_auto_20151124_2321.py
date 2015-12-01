# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0067_auto_20151124_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='keywords',
            field=models.TextField(null=True, blank=True),
        ),
    ]
