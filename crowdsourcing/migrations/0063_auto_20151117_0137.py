# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0062_userprofile_last_active'),
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
        migrations.AddField(
            model_name='userpreferences',
            name='data',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={b'login_alerts': b'email', b'feed_sorting': b'boomerang', b'language': b'EN'}),
        ),
    ]
