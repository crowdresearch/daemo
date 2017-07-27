import copy
from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.utils import create_copy
from rest_framework.exceptions import ValidationError


class TemplateItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.TemplateItem
        fields = ('id', 'name', 'type', 'sub_type', 'position', 'template', 'role', 'required', 'aux_attributes')

    def create(self, *args, **kwargs):
        item = models.TemplateItem.objects.create(**self.validated_data)
        item.group_id = item.id
        return item

    @staticmethod
    def create_revision(instance, template):
        instance.template = template
        return create_copy(instance=instance)


class TemplateSerializer(DynamicFieldsModelSerializer):
    items = TemplateItemSerializer(many=True, required=False, fields=('id', 'name', 'type', 'sub_type',
                                                                      'position', 'role', 'required',
                                                                      'aux_attributes',))

    class Meta:
        model = models.Template
        fields = ('id', 'name', 'items')
        read_only_fields = ('items', 'name')

    def create(self, with_defaults, is_review, *args, **kwargs):
        items = self.validated_data.pop('items') if 'items' in self.validated_data else []
        template = models.Template.objects.create(owner=kwargs['owner'], **self.validated_data)
        template.group_id = template.id
        if with_defaults:
            instructions_item = {
                "name": "item0",
                "icon": "title",
                "type": "instructions",
                "tooltip": "Instructions",
                "role": "display",
                "aux_attributes": {
                    "question": {
                        "value": "Instructions",
                        "data_source": None
                    }
                },
                "position": 1,
                "required": False,
                "template": template.id
            }
            item = {
                "type": "radio",
                "role": "input",
                "name": "item1",
                "icon": "radio_button_checked",
                "position": 2,
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
            instructions_item_serializer = TemplateItemSerializer(data=instructions_item)
            if template_item_serializer.is_valid() and instructions_item_serializer.is_valid():
                template_item_serializer.create()
                instructions_item_serializer.create()
                # else:
                #     raise ValidationError(template_item_serializer.errors)
        elif is_review:
            item = {
                "type": "radio",
                "role": "input",
                "name": "worker",
                "icon": "radio_button_checked",
                "position": 1,
                "template": template.id,
                "aux_attributes": {
                    "question": {
                        "value": "Choose the better submission",
                        "data_source": [{"type": "static", "value": "Choose the best submission", "position": 0}]
                    },
                    "layout": "column",
                    "options": [],
                    "shuffle_options": False
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

    @staticmethod
    def create_revision(instance):
        items = copy.copy(instance.items.all())
        template = create_copy(instance)

        for item in items:
            TemplateItemSerializer.create_revision(item, template)

        return template


class TemplateItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemplateItemProperties
