# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0032_auto_20150814_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='templateitem',
            name='position',
            field=models.IntegerField(default=0),
        ),
    ]
