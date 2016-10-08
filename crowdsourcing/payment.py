import stripe

from django.conf import settings
from crowdsourcing.models import StripeAccount


class Stripe(object):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    @staticmethod
    def create_account(user_id, country_iso, managed=True):
        account = stripe.Account.create(
            country=country_iso,
            managed=managed
        )
        customer = stripe.Customer.create(stripe_account=account)
        return StripeAccount.objects.create(owner_id=user_id, account_id=account['id'], customer_id=customer['id'],
                                            keys=None, managed=managed)

    @staticmethod
    def add_external_account(user, bank_or_cards):
        pass
