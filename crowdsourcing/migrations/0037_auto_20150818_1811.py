# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0036_auto_20150817_2226'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='templateitem',
            options={'ordering': ['position']},
        ),
    ]
