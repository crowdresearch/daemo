from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer


class TemplateItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.TemplateItem
        fields = ('id', 'id_string', 'name', 'role', 'icon', 'data_source', 'layout', 'type', 'label',
                  'values', 'position')


class TemplateSerializer(DynamicFieldsModelSerializer):
    template_items = TemplateItemSerializer(many=True)

    class Meta:
        model = models.Template
        fields = ('id', 'name', 'price', 'share_with_others', 'template_items')


class TemplateItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemplateItemProperties