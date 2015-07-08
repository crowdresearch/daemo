# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0004_auto_20150707_1227'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='hasMultipleTasks',
            new_name='has_multiple_tasks',
        ),
        migrations.AddField(
            model_name='project',
            name='save_to_drive',
            field=models.BooleanField(default=False),
        ),
    ]
