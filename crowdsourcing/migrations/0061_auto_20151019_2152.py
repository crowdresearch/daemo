# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0060_auto_20151019_2116'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='workerrequesterrating',
            index_together=set([('origin', 'target', 'last_updated', 'origin_type'), ('origin', 'target')]),
        ),
    ]
