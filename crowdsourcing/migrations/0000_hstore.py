# -*- coding: utf-8 -*-
from django.db import migrations
from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):
    dependencies = [
        ('crowdsourcing', '0073_auto_20151204_2310'),
    ]
    # run_before = [
    #     ('crowdsourcing', '0001_squashed_0063_auto_20151119_2242'),
    # ]

    operations = [
        HStoreExtension(),
    ]
