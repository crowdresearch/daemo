# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0060_auto_20151016_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='templateitem',
            name='sub_type',
        ),
    ]
