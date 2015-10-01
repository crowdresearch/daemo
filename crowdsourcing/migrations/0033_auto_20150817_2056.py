# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0032_auto_20150814_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerrequesterrating',
            name='module',
            field=models.ForeignKey(related_name='rating_module', default=1, to='crowdsourcing.Module'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workerrequesterrating',
            name='weight',
            field=models.FloatField(default=2, choices=[(1, b'BelowExpectations'), (2, b'MetExpectations'), (3, b'ExceedsExpectations')]),
        ),
    ]
