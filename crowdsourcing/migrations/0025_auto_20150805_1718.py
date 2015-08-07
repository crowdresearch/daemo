# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0024_file'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='File',
            new_name='RequesterInputFile',
        ),
    ]
