# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0050_submodule'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submodule',
            old_name='round',
            new_name='round_exp',
        ),
    ]
