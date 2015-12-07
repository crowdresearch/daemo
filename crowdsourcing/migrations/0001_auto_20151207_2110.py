# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crowdsourcing', '0000_hstore'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpreferences',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='userpreferences',
            name='language',
        ),
        migrations.RemoveField(
            model_name='userpreferences',
            name='login_alerts',
        ),
        migrations.RemoveField(
            model_name='userpreferences',
            name='user',
        ),
        migrations.AddField(
            model_name='userpreferences',
            name='data',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={b'login_alerts': b'email', b'feed_sorting': b'boomerang', b'language': b'EN'}),
        ),
        migrations.AddField(
            model_name='userpreferences',
            name='owner',
            field=models.OneToOneField(related_name='preferences', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
