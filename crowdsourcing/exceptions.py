from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class InsufficientFunds(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = _('Insufficient funds.')


def daemo_error(message, code=None):
    return {
        "type": "error",
        "message": message
    }
