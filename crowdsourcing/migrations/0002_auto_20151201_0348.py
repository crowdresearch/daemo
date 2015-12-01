# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsourcing', '0001_squashed_0063_auto_20151119_2242'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'general', max_length=16)),
                ('is_active', models.BooleanField(default=True)),
                ('balance', models.DecimalField(default=0, max_digits=19, decimal_places=4)),
                ('is_system', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(related_name='financial_accounts', to='crowdsourcing.UserProfile', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PayPalFlow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('paypal_id', models.CharField(max_length=128)),
                ('state', models.CharField(default=b'created', max_length=16)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('redirect_url', models.CharField(max_length=256)),
                ('payer_id', models.CharField(max_length=64, null=True)),
                ('recipient', models.ForeignKey(related_name='flow_recipient', to='crowdsourcing.FinancialAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=19, decimal_places=4)),
                ('state', models.CharField(default=b'created', max_length=16)),
                ('method', models.CharField(default=b'paypal', max_length=16)),
                ('sender_type', models.CharField(default=b'self', max_length=8)),
                ('reference', models.CharField(max_length=256, null=True)),
                ('currency', models.CharField(default=b'USD', max_length=4)),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('recipient', models.ForeignKey(related_name='transaction_recipient', to='crowdsourcing.FinancialAccount')),
                ('sender', models.ForeignKey(related_name='transaction_sender', to='crowdsourcing.FinancialAccount')),
            ],
        ),
        migrations.AlterField(
            model_name='conversationrecipient',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='workerrequesterrating',
            name='created_timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='workerrequesterrating',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
