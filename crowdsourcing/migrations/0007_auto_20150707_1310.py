# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0006_auto_20150707_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='owner',
            field=models.ForeignKey(to='crowdsourcing.UserProfile'),
        ),
    ]
