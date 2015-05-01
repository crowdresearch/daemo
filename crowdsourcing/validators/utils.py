from __future__ import unicode_literals
__author__ = 'dmorina'
from django.utils.translation import ugettext_lazy as _
from rest_framework.compat import unicode_to_repr
from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr
from csp import settings

class EqualityValidator(object):
    message = _('The fields {field_names} must be equal.')
    missing_message = _('This field is required.')

    def __init__(self, fields, message=None):
        self.fields = fields
        self.serializer_field = None
        self.message = message or self.message

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        self.instance = getattr(serializer, 'instance', None)
        self.initial_data = getattr(serializer,'initial_data', None)

    def __call__(self,*args, **kwargs):
        if self.initial_data.get(self.fields[0],'Password1') != self.initial_data.get(self.fields[1],'Password2'):
            field_names = ', '.join(self.fields)
            raise ValidationError(self.message.format(field_names=field_names))

class LengthValidator(object):
    message = _('Field {field_name} must be at least {length} characters long.')
    missing_message = _('This field is required.')

    def __init__(self, field, length,message=None):
        self.field = field
        self.length = length
        self.serializer_field = None
        self.message = message or self.message

    def set_context(self, serializer):
        self.initial_data = getattr(serializer,'initial_data', None)

    def __call__(self, *args, **kwargs):
        if len(self.initial_data[self.field]) < self.length:
            raise ValidationError(self.message.format(field_name=self.field, length=self.length))

class RegistrationAllowedValidator(object):
    message = _('Currently registrations are not allowed.')

    def __call__(self, *args, **kwargs):
        if not settings.REGISTRATION_ALLOWED:
            raise ValidationError(self.message)