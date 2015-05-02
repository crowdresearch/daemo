__author__ = 'elsabakiu'
__author__ = 'dmorina' 'neilthemathguy'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json

class WorkerSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerSkill


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Worker

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skill