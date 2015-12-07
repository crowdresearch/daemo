from django.db import migrations
from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):
    dependencies = [
        ('crowdsourcing', '0070_auto_20151203_2056'),
    ]
    # run_before = [
    #     ('crowdsourcing', '0001_squashed_0063_auto_20151119_2242'),
    # ]

    operations = [
        HStoreExtension(),
    ]
