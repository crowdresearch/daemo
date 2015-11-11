# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0062_userprofile_last_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'general', max_length=16)),
                ('is_active', models.BooleanField(default=True)),
                ('id_string', models.CharField(max_length=16)),
                ('balance', models.FloatField(default=0)),
                ('profile', models.ForeignKey(related_name='financial_account', to='crowdsourcing.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='PayPalFlow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('paypal_id', models.CharField(max_length=128)),
                ('state', models.CharField(default=b'created', max_length=16)),
                ('recipient', models.ForeignKey(related_name='flow_recipient', to='crowdsourcing.FinancialAccount')),
                ('sender', models.ForeignKey(related_name='flow_user', to='crowdsourcing.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_string', models.CharField(max_length=64)),
                ('amount', models.FloatField()),
                ('state', models.CharField(default=b'created', max_length=16)),
                ('method', models.CharField(default=b'PAYPAL', max_length=16)),
                ('sender_type', models.CharField(default=b'SELF', max_length=8)),
                ('reference', models.CharField(max_length=256, null=True)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('currency', models.ForeignKey(related_name='transaction_currency', to='crowdsourcing.Currency')),
                ('recipient', models.ForeignKey(related_name='transaction_recipient', to='crowdsourcing.FinancialAccount')),
                ('sender', models.ForeignKey(related_name='transaction_sender', to='crowdsourcing.FinancialAccount')),
            ],
        ),
    ]
