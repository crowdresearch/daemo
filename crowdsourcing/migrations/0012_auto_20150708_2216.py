# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0011_auto_20150708_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='module',
            field=models.ForeignKey(related_name='module_tasks', to='crowdsourcing.Module'),
        ),
    ]
