# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0002_auto_20150707_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='hasMultipleTasks',
            field=models.BooleanField(default=False),
        ),
    ]
