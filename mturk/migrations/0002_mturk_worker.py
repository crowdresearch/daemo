# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from crowdsourcing.utils import generate_random_id
from django.contrib.auth.hashers import make_password





def create_mturk_user(apps, schema_editor):
    user = apps.get_model("auth", "User")
    profile = apps.get_model("crowdsourcing", "UserProfile")
    worker = apps.get_model("crowdsourcing", "Worker")
    mturk_user = user.objects.create(username='mturk', email='mturk.worker@daemo.stanford.edu',
                                     password=make_password(generate_random_id()), is_active=False)
    mturk_profile = profile.objects.get_or_create(user=mturk_user)
    mturk_worker = worker.objects.get_or_create(profile=mturk_profile[0], alias='mturk')


class Migration(migrations.Migration):
    dependencies = [
        ('mturk', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_mturk_user),
    ]
