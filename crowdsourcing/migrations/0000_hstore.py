from django.db import migrations
from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):
    dependencies = []
    run_before = [
        ('crowdsourcing', '0001_initial'),
    ]
    operations = [
        HStoreExtension(),
    ]
