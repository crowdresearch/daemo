from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from crowdsourcing import models
from crowdsourcing.exceptions import InsufficientFunds


class ProjectValidator(object):
    message = _('Value \'{value}\' is not valid.')

    def __init__(self):
        self.initial_data = None
        self.instance = None

    def set_context(self, serializer):
        self.initial_data = getattr(serializer, 'initial_data', None)
        self.instance = getattr(serializer, 'instance', None)

    def __call__(self, value, *args, **kwargs):
        status = value.get('status', None)

        if self.instance is not None \
            and status is not None \
            and status != self.instance.status \
                and status == models.Project.STATUS_PUBLISHED:
            self.validate(value)

    def validate(self, value):
        num_rows = value.get('num_rows', 0)

        items = self.instance.template.items
        batch_files = self.instance.batch_files

        if items.count() == 0:
            raise ValidationError('At least one template item is required')

        has_input_item = False
        for item in items.all():
            if item.role == "input" or item.type == 'iframe':
                has_input_item = True
                break

        if not has_input_item:
            raise ValidationError('At least one input template item is required')

        if batch_files is not None and batch_files.count() > 0 \
            and self.has_csv_linkage(items) \
                and num_rows == 0:
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


def validate_account_balance(request, price, num_rows, repetition):
    requester_account = request.user.userprofile.financial_accounts.filter(type='requester', is_active=True).first()
    if price * num_rows * repetition > requester_account.balance:
        raise InsufficientFunds
