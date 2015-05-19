__author__ = 'elsabakiu'

from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json


class TaskPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task


class TaskWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskWorker
