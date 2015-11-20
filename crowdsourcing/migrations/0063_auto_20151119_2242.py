# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0062_userprofile_last_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='templateitem',
            name='sub_type',
        ),
        migrations.AddField(
            model_name='templateitem',
            name='label',
            field=models.TextField(null=True, blank=True),
        ),
    ]
