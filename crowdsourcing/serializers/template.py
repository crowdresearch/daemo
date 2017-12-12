import copy

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from crowdsourcing import models
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.utils import create_copy


class TemplateItemSerializer(DynamicFieldsModelSerializer):
    name = serializers.CharField(allow_blank=True)

    class Meta:
        model = models.TemplateItem
        fields = ('id', 'name', 'type', 'sub_type', 'template',
                  'role', 'required', 'aux_attributes', 'predecessor')

    def create(self, *args, **kwargs):
        item = models.TemplateItem.objects.create(**self.validated_data)
        item.group_id = item.id
        if item.type in ['radio', 'checkbox', 'select_list', 'file_upload', 'text']:
            item.role = models.TemplateItem.ROLE_INPUT
        item.save()
        return item

    @staticmethod
    def create_revision(instance, template):
        instance.template = template
        return create_copy(instance=instance)

    @staticmethod
    def rebuild_tree(template):
        items = models.TemplateItem.objects.prefetch_related('predecessor').filter(template_id=template.id)
        for item in items:
            if item.predecessor is not None:
                item.predecessor = items.filter(group_id=item.predecessor.group_id).first()
                item.save()


class TemplateSerializer(DynamicFieldsModelSerializer):
    items = TemplateItemSerializer(many=True, required=False, fields=('id', 'name', 'type', 'sub_type',
                                                                      'role', 'required',
                                                                      'aux_attributes', 'predecessor'))

    class Meta:
        model = models.Template
        fields = ('id', 'name', 'items')
        read_only_fields = ('items',)

    def create(self, with_defaults=True, is_review=False, *args, **kwargs):
        items = self.validated_data.pop('items') if 'items' in self.validated_data else []
        template = models.Template.objects.create(owner=kwargs['owner'], **self.validated_data)
        template.group_id = template.id
        if with_defaults:
            instructions_item = {
                "name": "",
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
                "name": "",
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
                instructions_item_object = instructions_item_serializer.create()

                item_obj = template_item_serializer.create()
                item_obj.predecessor = instructions_item_object
                item_obj.save()
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
        TemplateItemSerializer.rebuild_tree(template)
        return template


class TemplateItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemplateItemProperties
