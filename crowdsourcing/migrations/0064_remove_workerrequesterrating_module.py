# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0063_delete_requesterranking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workerrequesterrating',
            name='module',
        ),
    ]
