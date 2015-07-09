# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0008_auto_20150707_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='template',
        ),
        migrations.AlterField(
            model_name='module',
            name='project',
            field=models.ForeignKey(related_name='modules', to='crowdsourcing.Project'),
        ),
    ]
