# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0051_auto_20150914_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='submodule',
            name='result_per_round',
            field=models.IntegerField(default=1),
        ),
    ]
