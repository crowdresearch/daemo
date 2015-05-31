__author__ = 'elsabakiu'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Template


class TemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemplateItem


class TemplateItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemplateItemProperties