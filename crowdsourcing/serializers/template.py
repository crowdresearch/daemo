from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from rest_framework.exceptions import ValidationError


class TemplateItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.TemplateItem
        fields = ('id', 'name', 'type', 'sub_type', 'position', 'template', 'role', 'required', 'aux_attributes')

    def create(self, *args, **kwargs):
        item = models.TemplateItem.objects.create(**self.validated_data)
        return item


class TemplateSerializer(DynamicFieldsModelSerializer):
    template_items = TemplateItemSerializer(many=True, required=False, fields=('id', 'name', 'type', 'sub_type',
                                                                               'position', 'role', 'required',
                                                                               'aux_attributes',))

    class Meta:
        model = models.Template
        fields = ('id', 'name', 'template_items')
        read_only_fields = ('template_items', 'name')

    def create(self, with_defaults, *args, **kwargs):
        items = self.validated_data.pop('template_items') if 'template_items' in self.validated_data else []
        template = models.Template.objects.create(owner=kwargs['owner'], **self.validated_data)
        if with_defaults:
            item = {
                "type": "radio",
                "role": "input",
                "name": "radio_0",
                "icon": "radio_button_checked",
                "position": 1,
                "template": template.id,
                "aux_attributes": {
                    "question": {
                        "data_source": None,
                        "value": "Untitled Question",
                    },
                    "layout": 'column',
                    "options": [
                        {
                            "data_source": None,
                            "value": 'Option 1',
                            "position": 1
                        },
                        {
                            "data_source": None,
                            "value": 'Option 2',
                            "position": 2
                        }
                    ],
                    "shuffle_options": "false"
                },
            }
            template_item_serializer = TemplateItemSerializer(data=item)
            if template_item_serializer.is_valid():
                template_item_serializer.create()
            else:
                raise ValidationError(template_item_serializer.errors)
        else:
            for item in items:
                item.update({"template": template.id})
                template_item_serializer = TemplateItemSerializer(data=item)
                if template_item_serializer.is_valid():
                    template_item_serializer.create()
                else:
                    raise ValidationError(template_item_serializer.errors)

        return template


class TemplateItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemplateItemProperties
