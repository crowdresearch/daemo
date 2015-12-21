from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError


class EqualityValidator(object):
    message = _('The fields {field_names} must be equal.')
    missing_message = _('This field is required.')

    def __init__(self, fields, message=None):
        self.fields = fields
        self.serializer_field = None
        self.message = message or self.message
        self.instance = None
        self.initial_data = None
        self.validate_non_fields = False

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        self.instance = getattr(serializer, 'instance', None)
        self.initial_data = getattr(serializer, 'initial_data', None)
        self.validate_non_fields = getattr(serializer, 'validate_non_fields', False)

    def __call__(self, *args, **kwargs):
        if self.validate_non_fields:
            if self.fields[0] not in self.initial_data or self.fields[1] not in self.initial_data:
                raise ValidationError("Both fields are required.")
            if self.initial_data.get(self.fields[0], 'Password1') != self.initial_data.get(self.fields[1],
                                                                                           'Password2'):
                field_names = ', '.join(self.fields)
                raise ValidationError(self.message.format(field_names=field_names))


class LengthValidator(object):
    message = _('Field {field_name} must be at least {length} characters long.')
    missing_message = _('Field {field_name} is required.')

    def __init__(self, field, length, message=None):
        self.field = field
        self.length = length
        self.serializer_field = None
        self.message = message or self.message
        self.initial_data = None
        self.validate_non_fields = False

    def set_context(self, serializer):
        self.initial_data = getattr(serializer, 'initial_data', None)
        self.validate_non_fields = getattr(serializer, 'validate_non_fields', False)

    def __call__(self, *args, **kwargs):
        if self.validate_non_fields:
            if self.field not in self.initial_data:
                raise ValidationError(self.missing_message.format(field_name=self.field))
            if len(self.initial_data[self.field]) < self.length:
                raise ValidationError(self.message.format(field_name=self.field, length=self.length))


class InequalityValidator(object):
    message = _('Field {field_name} must be {field_operator} than {field_value}.')

    def __init__(self, field, value, operator, message=None):
        self.field = field
        self.value = value
        self.operator = 'gt'
        self.message = message or self.message
        self.initial_data = None

    def set_context(self, serializer):
        self.initial_data = getattr(serializer, 'initial_data', None)

    def __call__(self, *args, **kwargs):
        if self.initial_data[self.field] >= self.value and self.operator == 'lt':
            raise ValidationError(self.message.format(field_name=self.field,
                                                      field_operator='less', field_value=self.value))
        elif self.initial_data[self.field] <= self.value and self.operator == 'gt':
            raise ValidationError(self.message.format(field_name=self.field,
                                                      field_operator='greater', field_value=self.value))


class ConditionallyRequiredValidator(object):
    message = _('Field {field2_name} is required because {field_name} is {type_value}.')

    def __init__(self, field, value, field2, message=None):
        self.field = field
        self.value = value
        self.field2 = field2
        self.message = message or self.message
        self.initial_data = None

    def set_context(self, serializer):
        self.initial_data = getattr(serializer, 'initial_data', None)

    def __call__(self, *args, **kwargs):
        if self.initial_data[self.field] == self.value and self.field2 not in self.initial_data:
            raise ValidationError(self.message.format(field_name=self.field, field2_name=self.field2,
                                                      type_value=self.value))
