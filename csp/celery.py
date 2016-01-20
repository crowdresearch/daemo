from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from django.apps import apps
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csp.settings')
app = Celery('csp')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(['crowdsourcing', 'mturk'])



