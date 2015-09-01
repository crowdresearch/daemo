# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0044_auto_20150828_1857'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workerrequesterrating',
            old_name='type',
            new_name='origin_type',
        ),
    ]
