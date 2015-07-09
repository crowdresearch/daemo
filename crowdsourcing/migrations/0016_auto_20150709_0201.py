# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crowdsourcing', '0015_auto_20150709_0149'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversationRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1)),
                ('message', models.ForeignKey(to='crowdsourcing.Conversation')),
                ('recipient', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='messagerecipient',
            name='message',
        ),
        migrations.RemoveField(
            model_name='messagerecipient',
            name='recipient',
        ),
        migrations.DeleteModel(
            name='MessageRecipient',
        ),
    ]
