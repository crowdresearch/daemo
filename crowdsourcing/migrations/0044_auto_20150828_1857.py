# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0043_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskworkerresult',
            name='result',
            field=models.TextField(null=True),
        ),
    ]
