__author__ = 'elsabakiu'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
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

class TemplateRestrictedSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model = models.Template
		fields = ('id', 'source_html')

class TemplateItemRestrictedSerializer(DynamicFieldsModelSerializer):
	template = TemplateRestrictedSerializer()
	class Meta:
		model = models.TemplateItem
		fields = ('id', 'name', 'template')