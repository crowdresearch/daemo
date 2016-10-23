import hashlib

import stripe
import time

from django.conf import settings
from django.utils import timezone

from crowdsourcing.models import StripeAccount, StripeCustomer, StripeTransfer, StripeCharge, StripeRefund, \
    StripeTransferReversal


class Stripe(object):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    @staticmethod
    def _get_idempotency_key(s):
        key_hash = hashlib.sha512()
        key_hash.update(unicode(s))
        return key_hash.hexdigest()

    @staticmethod
    def _create_customer(source, email):
        customer = stripe.Customer.create(
            source=source,
            email=email
        )
        return customer

    def _create_account(self, country_iso, email, ip_address, birthday, first_name, last_name, managed=True):

        if birthday is None:
            raise Exception("Birthday is missing!")

        account = stripe.Account.create(
            country=country_iso,
            managed=managed,
            email=email,
            idempotency_key=self._get_idempotency_key(email)
        )
        account.tos_acceptance.date = int(time.time())
        account.tos_acceptance.ip = ip_address
        account.transfer_statement_descriptor = 'Daemo payout'
        account.legal_entity.type = 'individual'
        account.legal_entity.dob.day = birthday.day
        account.legal_entity.dob.month = birthday.month
        account.legal_entity.dob.year = birthday.year
        account.legal_entity.first_name = first_name
        account.legal_entity.last_name = last_name
        account.save()

        return account

    def create_account_and_customer(self, user, country_iso, ip_address, is_worker=False, is_requester=False,
                                    credit_card=None, bank=None):
        account_obj = None
        customer_obj = None
        if is_worker:
            account = self._create_account(country_iso=country_iso, email=user.email, ip_address=ip_address,
                                           birthday=user.profile.birthday, first_name=user.first_name,
                                           last_name=user.last_name)
            account_obj = StripeAccount.objects.create(owner_id=user.id, stripe_id=account.stripe_id)
            if bank is None:
                raise Exception("Bank information missing!")
            if "account_number" not in bank or "routing_number" not in bank:
                raise Exception("Account number and routing number required.")
            if "currency" not in bank or "country" not in bank:
                raise Exception("Country and currency required.")
            external_account = bank
            external_account.update({'object': 'bank_account'})
            self._update_external_account(external_account=external_account, stripe_id=user.stripe_account.stripe_id,
                                          stripe_account=account)

        if is_requester:
            if credit_card is None:
                raise Exception("Credit card missing!")
            if 'number' not in credit_card or 'exp_year' not in credit_card or 'exp_month' not in credit_card:
                raise Exception("Invalid credit card.")
            source = {
                'object': 'card',
                'exp_month': credit_card['exp_month'],
                'exp_year': credit_card['exp_year'],
                'number': credit_card['number'],
                'cvc': credit_card['cvc']
            }
            customer = self._create_customer(source, user.email)
            customer_obj = StripeCustomer.objects.create(owner_id=user.id, stripe_id=customer.stripe_id)
        return account_obj, customer_obj

    @staticmethod
    def _update_external_account(stripe_id, external_account, stripe_account=None):
        account = stripe_account or stripe.Account.retrieve(stripe_id)
        account.external_account = external_account
        account.save()

    @staticmethod
    def _update_customer_source(source, stripe_id, stripe_customer):
        customer = stripe_customer or stripe.Customer.retrieve(stripe_id)
        customer.source = source
        customer.save()

    @staticmethod
    def refund(charge, amount):
        stripe_charge = stripe.Charge(charge.stripe_id)
        refund = stripe_charge.refunds.create(amount)
        return StripeRefund.objects.create(charge=charge, stripe_id=refund.stripe_id)

    @staticmethod
    def _transfer(amount, destination_account, idempotency_key=None, source_transaction=None):
        transfer = stripe.Transfer.create(
            amount=amount,
            currency="usd",
            destination=destination_account,
            idempotency_key=idempotency_key,
            source_transaction=source_transaction
        )

        return transfer

    def transfer(self, user, amount, idempotency_key=None):
        transfer = self._transfer(amount=amount, idempotency_key=idempotency_key,
                                  destination_account=user.stripe_account.stripe_id)
        stripe_data = {
            "amount": amount,
            "status": transfer.status
        }
        return StripeTransfer.objects.create(stripe_id=transfer.stripe_id, destination=user, stripe_data=stripe_data)

    @staticmethod
    def _reverse_transfer(transfer_id, amount):
        transfer = stripe.Transfer.retrieve(transfer_id)
        reversal = transfer.reversals.create(
            amount=amount,
            refund_application_fee=True
        )
        return reversal

    def reverse_transfer(self, transfer, amount):
        stripe_transfer = self._reverse_transfer(transfer.stripe_id, amount)
        return StripeTransferReversal.objects.create(stripe_id=stripe_transfer.stripe_id, transfer=transfer)

    @staticmethod
    def _create_charge(customer_id, amount, application_fee=0):
        charge = stripe.Charge.create(
            amount=amount,
            currency="usd",
            customer=customer_id,
            application_fee=application_fee
        )
        return charge

    def create_charge(self, amount, user):
        application_fee = self.get_chargeback_fee(amount)
        charge = self._create_charge(customer_id=user.stripe_customer.stripe_id, amount=amount,
                                     application_fee=application_fee)
        stripe_data = {
            "amount": amount,
            "status": charge.status
        }
        return StripeCharge.objects.create(stripe_id=charge.stripe_id, customer=user.stripe_customer,
                                           stripe_data=stripe_data, balance=amount)

    def pay_worker(self, task_worker):
        amount = task_worker.task.project.price * 100
        source_charge = task_worker.task.project.owner \
            .stripe_customer.charges.filter(expired=False,
                                            balance__gt=amount).order_by('id').first()
        self.transfer(task_worker.worker, amount,
                      idempotency_key=self._get_idempotency_key(task_worker.id))

        source_charge.balance -= amount
        source_charge.save()
        task_worker.charge = source_charge
        task_worker.is_paid = True
        task_worker.paid_at = timezone.now()
        task_worker.save()

    @staticmethod
    def get_chargeback_fee(amount):
        return amount * settings.DAEMO_CHARGEBACK_FEE
