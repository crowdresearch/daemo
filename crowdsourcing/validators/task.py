from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from crowdsourcing.models import TemplateItem
import re


class ItemValidator(object):
    message = _('Value \'{value}\' is not valid.')

    def __init__(self):
        self.initial_data = None

    def set_context(self, serializer):
        self.initial_data = getattr(serializer, 'initial_data', None)

    def __call__(self, *args, **kwargs):
        template_item = TemplateItem.objects.get(id=self.initial_data[0]['template_item'])
        result = self.initial_data[0]['result']
        if template_item.role == TemplateItem.ROLE_INPUT and 'pattern' in template_item.aux_attributes:
            if not re.match(template_item.aux_attributes['pattern'], result):
                raise ValidationError(self.message.format(value=result))
        return True
