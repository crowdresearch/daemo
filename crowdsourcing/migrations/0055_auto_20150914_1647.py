# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0054_submodule_hours_before_results'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submodule',
            name='module',
        ),
        migrations.AddField(
            model_name='submodule',
            name='fake_module',
            field=models.ForeignKey(related_name='fake_module', default=2, to='crowdsourcing.Module'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submodule',
            name='origin_module',
            field=models.ForeignKey(related_name='origin_module', default=12, to='crowdsourcing.Module'),
            preserve_default=False,
        ),
    ]
