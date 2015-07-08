# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0010_auto_20150707_2247'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modulereview',
            old_name='annonymous',
            new_name='anonymous',
        ),
        migrations.AddField(
            model_name='task',
            name='data',
            field=models.TextField(null=True),
        ),
    ]
