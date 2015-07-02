# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0002_auto_20150619_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='alias',
            field=models.CharField(default='schmoe', max_length=20, error_messages={b'required': b'Please enter an alias!'}),
            preserve_default=False,
        ),
    ]
