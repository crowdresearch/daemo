# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0020_auto_20150709_0229'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='projectrequester',
            unique_together=set([('requester', 'project')]),
        ),
        migrations.AlterUniqueTogether(
            name='workerskill',
            unique_together=set([('worker', 'skill')]),
        ),
    ]
