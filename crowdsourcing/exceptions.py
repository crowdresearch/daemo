from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class InsufficientFunds(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = _('Insufficient funds.')


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Bad request.')
    default_code = 'bad_request'

    def __init__(self, detail, *args, **kwargs):
        self.default_detail = detail
        super(BadRequest, self).__init__(*args, **kwargs)
