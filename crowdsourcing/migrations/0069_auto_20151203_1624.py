# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0068_auto_20151124_2321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='template',
        ),
        migrations.RemoveField(
            model_name='templateitem',
            name='role',
        ),
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Draft'), (2, b'Saved'), (3, b'Published'), (4, b'Completed'), (5, b'Paused')]),
        ),
        migrations.AlterField(
            model_name='moduletemplate',
            name='module',
            field=models.ForeignKey(related_name='module_template', to='crowdsourcing.Module'),
        ),
        migrations.AlterField(
            model_name='templateitem',
            name='icon',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='moduletemplate',
            unique_together=set([('module', 'template')]),
        ),
    ]
