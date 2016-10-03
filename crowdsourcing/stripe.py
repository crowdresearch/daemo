import stripe

from django.conf import settings
from crowdsourcing.models import StripeAccount


class Stripe(object):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    @staticmethod
    def create_account(user, country_iso, managed=True):
        account = stripe.Account.create(
            country=country_iso,
            managed=managed,
            display_name=user.username,
            email=user.email
        )
        return StripeAccount.objects.create(owner=user, stripe_id=account['id'], keys=None, managed=managed)

    @staticmethod
    def add_external_account(user, bank_or_cards):
        pass

