# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crowdsourcing', '0063_auto_20151117_0137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpreferences',
            name='user',
        ),
        migrations.AddField(
            model_name='userpreferences',
            name='owner',
            field=models.OneToOneField(related_name='preferences', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
