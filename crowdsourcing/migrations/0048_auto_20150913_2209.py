# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0047_auto_20150913_1148'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModulePool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pool', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'In Review'), (3, b'In Progress'), (4, b'Completed'), (5, b'Paused')]),
        ),
        migrations.AddField(
            model_name='modulepool',
            name='module',
            field=models.ForeignKey(related_name='module_pool', to='crowdsourcing.Module'),
        ),
    ]
