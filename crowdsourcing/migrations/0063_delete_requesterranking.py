# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0013_auto_20151221_2208'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RequesterRanking',
        ),
    ]
