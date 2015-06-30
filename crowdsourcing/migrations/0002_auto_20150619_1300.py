# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import oauth2client.django_orm


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crowdsourcing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('type', models.CharField(max_length=16)),
                ('email', models.EmailField(max_length=254)),
                ('access_token', models.TextField(max_length=2048)),
                ('root', models.CharField(max_length=256)),
                ('is_active', models.IntegerField()),
                ('quota', models.BigIntegerField()),
                ('used_space', models.BigIntegerField()),
                ('assigned_space', models.BigIntegerField()),
                ('status', models.IntegerField(default=models.BigIntegerField())),
            ],
        ),
        migrations.CreateModel(
            name='CredentialsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credential', oauth2client.django_orm.CredentialsField(null=True)),
                ('account', models.ForeignKey(to='crowdsourcing.AccountModel')),
            ],
        ),
        migrations.CreateModel(
            name='FlowModel',
            fields=[
                ('id', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('flow', oauth2client.django_orm.FlowField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemporaryFlowModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=16)),
                ('email', models.EmailField(max_length=254)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='module',
            name='price',
        ),
        migrations.AddField(
            model_name='task',
            name='price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'In Review'), (3, b'In Progress'), (4, b'Finished')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'Accepted'), (3, b'Assigned'), (4, b'Finished')]),
        ),
        migrations.AlterField(
            model_name='taskworkerresult',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Created'), (2, b'Accepted'), (3, b'Rejected')]),
        ),
        migrations.AddField(
            model_name='accountmodel',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
