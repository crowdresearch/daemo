from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from rest_framework.exceptions import ValidationError


class TemplateItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.TemplateItem
        fields = ('id', 'name', 'type', 'position', 'template', 'role', 'required', 'aux_attributes')

    def create(self, *args, **kwargs):
        item = models.TemplateItem.objects.create(**self.validated_data)
        return item


class TemplateSerializer(DynamicFieldsModelSerializer):
    template_items = TemplateItemSerializer(many=True, required=False)

    class Meta:
        model = models.Template
        fields = ('id', 'name', 'template_items')
        read_only_fields = ('template_items',)

    def create(self, with_default, *args, **kwargs):
        template = models.Template.objects.create(owner=kwargs['owner'], **self.validated_data)
        if with_default:
            item = {
                "type": "radio",
                "values": "Option 1,Option 2,Option 3",
                "label": "Add question here",
                "data_source": None,
                "role": "input",
                "layout": "row",
                "id_string": "radio_0",
                "name": "radio_0",
                "icon": "radio_button_checked",
                "position": 1,
                "template": template.id
            }
            template_item_serializer = TemplateItemSerializer(data=item)
            if template_item_serializer.is_valid():
                template_item_serializer.create()
            else:
                raise ValidationError(template_item_serializer.errors)
        return template


class TemplateItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemplateItemProperties
