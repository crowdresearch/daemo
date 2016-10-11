import stripe

from django.conf import settings
from crowdsourcing.models import StripeAccount, StripeCustomer


class Stripe(object):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Stripe.create_account_and_customer(user_id=user.id, country_iso=user_profile.address.city.country.code)
    @staticmethod
    def create_account_and_customer(user_id, country_iso, is_worker=False, is_requester=False):
        account_obj = None
        customer_obj = None
        if is_worker:
            account = stripe.Account.create(
                country=country_iso,
                managed=True
            )
            account_obj = StripeAccount.objects.create(owner_id=user_id, account_id=account['id'])
        if is_requester:
            customer = stripe.Customer.create()
            customer_obj = StripeCustomer.objects.create(owner_id=user_id, customer_id=customer['id'])
        return account_obj, customer_obj

    @staticmethod
    def add_external_account(user, bank_or_cards):
        account = stripe.Account.retrieve(user.stripe_account.stripe_id)
        account.external_accounts.create(external_account="btok_9CUY3ZiKZEHSlb")

    @staticmethod
    def refund(user, amount):
        pass

