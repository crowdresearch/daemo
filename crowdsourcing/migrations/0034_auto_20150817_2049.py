# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0033_templateitem_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templateitem',
            name='position',
            field=models.IntegerField(),
        ),
    ]
