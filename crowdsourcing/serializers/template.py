__author__ = 'elsabakiu'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
import json

class TemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemplateItem
        fields = ('id', 'id_string', 'name', 'role', 'icon', 'data_source', 'layout', 'sub_type', 'type', 'values')


class TemplateSerializer(serializers.ModelSerializer):
	template_items = TemplateItemSerializer(many=True)
	
	class Meta:
		model = models.Template
		fields = ('id', 'name', 'price', 'share_with_others', 'template_items')


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