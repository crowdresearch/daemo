# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0007_auto_20150707_1310'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module', models.ForeignKey(to='crowdsourcing.Module')),
                ('template', models.ForeignKey(to='crowdsourcing.Template')),
            ],
        ),
        migrations.AlterField(
            model_name='templateitem',
            name='template',
            field=models.ForeignKey(related_name='template_items', to='crowdsourcing.Template'),
        ),
        migrations.AddField(
            model_name='module',
            name='template',
            field=models.ManyToManyField(to='crowdsourcing.Template', through='crowdsourcing.ModuleTemplate'),
        ),
    ]
