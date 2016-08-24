# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_system_financial_account(apps, schema_editor):
    account = apps.get_model("crowdsourcing", "FinancialAccount")
    account.objects.get_or_create(is_system=True, type=3)


class Migration(migrations.Migration):
    dependencies = [
        ('crowdsourcing', '0076_paypalpayoutlog'),
    ]

    operations = [
        migrations.RunPython(create_system_financial_account),
    ]
