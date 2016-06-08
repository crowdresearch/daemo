from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError


class ProjectValidator(object):
    message = _('Value \'{value}\' is not valid.')

    def __init__(self):
        self.initial_data = None
        self.instance = None

    def set_context(self, serializer):
        self.initial_data = getattr(serializer, 'initial_data', None)
        self.instance = getattr(serializer, 'instance', None)

    def __call__(self, value, *args, **kwargs):
        status = value.get('status', self.instance.status)

        if self.instance.status != status and status == 2:
            self.validate_template_items(self.instance.template.items, value)

    def validate_template_items(self, items, value):
        num_rows = value.get('num_rows', 0)

        if items.count() == 0:
            raise ValidationError('At least one template item is required')

        has_input_item = False
        for item in items.all():
            if item.role == "input" or item.type == 'iframe':
                has_input_item = True
                break

        if not has_input_item:
            raise ValidationError('At least one input template item is required')

        if self.instance.batch_files.count() > 0 and self.has_csv_linkage(
                self.instance.template.items):
            if num_rows == 0:
                raise ValidationError('Number of tasks should be greater than 0')

    def has_csv_linkage(self, items):
        if items.count() > 0:
            template_items = items.all()
            for item in template_items:
                attribs = item.aux_attributes

                if 'question' in attribs \
                        and 'data_source' in attribs['question'] \
                        and attribs['question']['data_source'] is not None:
                    for source in attribs['question']['data_source']:
                        if source['type'] == 'dynamic':
                            return True

                if 'options' in attribs and attribs['options'] is not None:
                    for option in attribs['options']:
                        if 'data_source' in option and option['data_source'] is not None:
                            for source in option['data_source']:
                                if source['type'] == 'dynamic':
                                    return True
        return False
