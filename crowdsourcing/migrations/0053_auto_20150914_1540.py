# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0052_submodule_result_per_round'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submodule',
            old_name='result_per_round',
            new_name='results_per_round',
        ),
    ]
