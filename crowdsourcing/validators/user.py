from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError


class AllowedPreferencesValidator(object):
    invalid_key_message = _('The field {field_name} is not a valid preference.')
    invalid_value_message = _('The value {field_value} is not valid for field {field_name}.')

    def __init__(self, field):
        self.initial_data = None
        self.field = field
        self.instance = None
        self.allowed_preferences = ['language', 'feed_sorting', 'login_alerts']
        self.allowed_values = {
            'language': ['EN'],
            'login_alerts': ['email', 'sms', 'none'],
            'feed_sorting': ['boomerang', 'publish_date']
        }

    def set_context(self, serializer):
        self.instance = getattr(serializer, 'instance', None)
        self.initial_data = getattr(serializer, 'initial_data', None)

    def __call__(self, *args, **kwargs):
        preferences = self.initial_data[self.field]
        for key in preferences:
            if key not in self.allowed_preferences:
                raise ValidationError(self.invalid_key_message.format(field_name=key))
            if preferences[key] not in self.allowed_values[key]:
                raise ValidationError(self.invalid_value_message.format(field_name=self.field,
                                                                        field_value=preferences[key]))
