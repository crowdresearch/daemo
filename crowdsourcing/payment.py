from __future__ import division

import hashlib
import math
import time

import stripe
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from crowdsourcing.exceptions import daemo_error
from crowdsourcing.models import StripeAccount, StripeCustomer, StripeTransfer, StripeCharge, StripeRefund, \
    StripeTransferReversal, WorkerBonus
from crowdsourcing.utils import is_discount_eligible


class Stripe(object):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe.api_version = '2017-02-14'

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

    def _create_account(self, country_iso, email, ip_address, birthday, first_name, last_name, city, street,
                        postal_code, state, ssn_last_4=None, managed=True):

        if birthday is None:
            raise serializers.ValidationError(detail=daemo_error("Birthday is missing!"))

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
        account.legal_entity.address.city = city
        account.legal_entity.address.line1 = street
        account.legal_entity.address.postal_code = postal_code
        account.legal_entity.address.state = state
        account.legal_entity.ssn_last_4 = ssn_last_4
        account.save()

        return account

    def create_account_and_customer(self, user, country_iso, ip_address, is_worker=False, is_requester=False,
                                    credit_card=None, bank=None, ssn_last_4=None):
        account_obj = None
        customer_obj = None
        if is_worker:
            if not hasattr(user, 'stripe_account') or user.stripe_account is None:
                if country_iso == 'US' and ssn_last_4 is None:
                    raise serializers.ValidationError(detail=daemo_error("Last 4 digits of your SSN are required."))
                try:
                    account = self._create_account(country_iso=country_iso, email=user.email, ip_address=ip_address,
                                                   birthday=user.profile.birthday, first_name=user.first_name,
                                                   last_name=user.last_name, city=user.profile.address.city.name,
                                                   postal_code=user.profile.address.postal_code,
                                                   state=user.profile.address.city.state_code, ssn_last_4=ssn_last_4,
                                                   street=user.profile.address.street)
                except stripe.InvalidRequestError as e:
                    raise serializers.ValidationError(detail=daemo_error(e.message))
                stripe_data = {
                    "default_bank": {
                        "last_4": bank.get('account_number')[-4:] if bank is not None else None,
                        "name": None
                    },
                    "display_name": account.display_name,
                    # "external_accounts": account.external_accounts,
                    "details_submitted ": account.details_submitted,
                    "ssn_last_4_provided": account.legal_entity.ssn_last_4_provided,
                    "verification": account.verification,
                    "managed": account.managed,
                    "transfer_schedule": account.transfer_schedule,
                    "transfer_statement_descriptor": account.transfer_statement_descriptor,
                    "transfers_enabled ": account.transfers_enabled
                }
                account_obj = StripeAccount.objects.create(owner_id=user.id, stripe_id=account.stripe_id,
                                                           stripe_data=stripe_data)
                if bank is None:
                    raise serializers.ValidationError(detail=daemo_error("Bank information missing!"))
                if "account_number" not in bank or "routing_number" not in bank:
                    raise serializers.ValidationError(detail=daemo_error("Account number and routing "
                                                                         "number required."))
                if "currency" not in bank or "country" not in bank:
                    raise serializers.ValidationError(detail=daemo_error("Country and currency required."))
                external_account = bank
                external_account.update({'object': 'bank_account'})
                try:
                    self._update_external_account(external_account=external_account,
                                                  stripe_id=account_obj.stripe_id,
                                                  stripe_account=None)
                except stripe.InvalidRequestError as e:
                    raise serializers.ValidationError(detail=daemo_error(e.message))
            else:
                account_obj = user.stripe_account

        if is_requester:
            self._validate_credit_card(credit_card=credit_card)
            source = {
                'object': 'card',
                'exp_month': credit_card['exp_month'],
                'exp_year': credit_card['exp_year'],
                'number': credit_card['number'],
                'cvc': credit_card['cvv']
            }
            try:
                if not hasattr(user, 'stripe_customer') or user.stripe_customer is None:
                    customer = self._create_customer(source, user.email)
                    stripe_data = {
                        "default_source": customer.default_source,
                        "livemode": customer.livemode,
                        "default_card": {
                            "name": None,
                            "exp_month": credit_card['exp_month'],
                            "exp_year": credit_card['exp_year'],
                            "last_4": credit_card['number'][-4:]
                        }
                    }
                    customer_obj = StripeCustomer.objects.create(owner_id=user.id, stripe_id=customer.stripe_id,
                                                                 stripe_data=stripe_data, account_balance=500)
                else:
                    customer_obj = user.stripe_customer
            except stripe.CardError as e:
                raise serializers.ValidationError(detail=daemo_error(e.message))
        return account_obj, customer_obj

    @staticmethod
    def _validate_credit_card(credit_card):
        if credit_card is None:
            raise serializers.ValidationError(detail=daemo_error("Credit card missing!"))
        if 'number' not in credit_card or 'exp_year' not in credit_card or 'exp_month' not in credit_card:
            raise serializers.ValidationError(detail=daemo_error("Invalid credit card!"))

    @staticmethod
    def _validate_bank(bank):
        if bank is None:
            raise serializers.ValidationError(detail=daemo_error("Bank information missing!"))
        if "account_number" not in bank or "routing_number" not in bank:
            raise serializers.ValidationError(detail=daemo_error("Account number and routing "
                                                                 "number required."))
        if "currency" not in bank or "country" not in bank:
            raise serializers.ValidationError(detail=daemo_error("Country and currency required."))

    @staticmethod
    def _update_external_account(stripe_id, external_account, stripe_account=None):
        account = stripe_account or stripe.Account.retrieve(stripe_id)
        account.external_account = external_account
        account.save()
        return account

    @staticmethod
    def _update_customer_source(source, stripe_id, stripe_customer):
        customer = stripe_customer or stripe.Customer.retrieve(stripe_id)
        customer.source = source
        customer.save()
        return customer

    def update_external_account(self, bank, user):
        self._validate_bank(bank=bank)
        external_account = bank
        external_account.update({'object': 'bank_account'})
        self._update_external_account(stripe_id=user.stripe_account.stripe_id,
                                      external_account=external_account)
        user.stripe_account.stripe_data['default_bank'].update({
            "last_4": bank.get('account_number')[-4:] if bank is not None else None,
            "name": None
        })
        user.stripe_account.save()
        return user.stripe_account

    def update_customer_source(self, credit_card, user):
        self._validate_credit_card(credit_card=credit_card)
        source = {
            'object': 'card',
            'exp_month': credit_card['exp_month'],
            'exp_year': credit_card['exp_year'],
            'number': credit_card['number'],
            'cvc': credit_card['cvv']
        }
        self._update_customer_source(source=source, stripe_id=user.stripe_customer.stripe_id, stripe_customer=None)
        user.stripe_customer.stripe_data.update({"default_card": {
            "name": None,
            "exp_month": credit_card['exp_month'],
            "exp_year": credit_card['exp_year'],
            "last_4": credit_card['number'][-4:]
        }})
        user.stripe_customer.save()
        return user.stripe_customer

    @staticmethod
    def refund(charge, amount):
        stripe_charge = stripe.Charge(charge.stripe_id)
        refund = stripe_charge.refunds.create(amount)
        charge.customer.account_balance -= amount
        charge.customer.save()
        return StripeRefund.objects.create(charge=charge, stripe_id=refund.stripe_id)

    @staticmethod
    def _transfer(amount, destination_account, idempotency_key=None, source_transaction=None, description=None):
        transfer = stripe.Transfer.create(
            amount=amount,
            currency="usd",
            destination=destination_account,
            idempotency_key=idempotency_key,
            source_transaction=source_transaction,
            description=description
        )

        return transfer

    def transfer(self, user, amount, idempotency_key=None, description=None):
        transfer = self._transfer(amount=amount, idempotency_key=idempotency_key,
                                  destination_account=user.stripe_account.stripe_id, description=description)
        stripe_data = {
            "amount": amount,
            "status": transfer.status,
            "description": description
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
    def _create_charge(customer_id, amount, description, application_fee=0):
        charge = stripe.Charge.create(
            amount=amount,
            currency="usd",
            customer=customer_id,
            description=description
            # application_fee=application_fee
        )
        return charge

    def create_charge(self, amount, user):
        application_fee = self.get_chargeback_fee(amount)
        discount_applied = is_discount_eligible(user)
        if discount_applied:
            f = 0.5
        else:
            f = 1
        amount_to_charge = int(math.ceil((amount * f + 30) / 0.966))  # 2.9% + 30c + 0.5%
        description = "Daemo crowdsourcing prepaid tasks for {} {}".format(user.first_name, user.last_name)
        charge = self._create_charge(customer_id=user.stripe_customer.stripe_id, amount=amount_to_charge,
                                     application_fee=application_fee, description=description)
        stripe_data = {
            "amount": int(amount),
            "status": charge.status,
            "description": description
        }
        # amount_total = int(amount - 0.029 * amount - 30 - self.get_chargeback_fee(amount))
        user.stripe_customer.account_balance += amount
        user.stripe_customer.save()

        return StripeCharge.objects.create(stripe_id=charge.stripe_id, customer=user.stripe_customer,
                                           stripe_data=stripe_data, balance=int(math.ceil(amount * f)),
                                           discount_applied=discount_applied,
                                           raw_amount=amount_to_charge, discount=f)

    def pay_worker(self, task_worker):
        amount = int(task_worker.task.price * 100) if task_worker.task.price is not None else int(
            task_worker.task.project.price * 100)
        source_charge = task_worker.task.project.owner \
            .stripe_customer.charges.filter(expired=False,
                                            balance__gt=amount).order_by('id').first()

        self.transfer(task_worker.worker, amount,
                      idempotency_key=self._get_idempotency_key(task_worker.id))
        task_worker.charge = source_charge
        task_worker.is_paid = True
        task_worker.paid_at = timezone.now()
        task_worker.save()
        # TODO fix balance bug
        if source_charge is None:
            return 'NO_CHARGE_FOUND'
        else:
            source_charge.balance -= amount
            source_charge.save()

    def pay_bonus(self, worker, user, amount, reason):
        amount = int(amount * 100)
        source_charge = user.stripe_customer.charges.filter(expired=False,
                                                            balance__gte=amount).order_by('id').first()
        self.transfer(worker, amount, description=reason)
        user.stripe_customer.account_balance -= amount
        user.stripe_customer.save()

        if source_charge is not None:
            source_charge.balance -= amount
            source_charge.save()
        bonus = WorkerBonus.objects.create(worker=worker, requester=user, reason=reason, amount=amount,
                                           charge=source_charge)
        return bonus

    @staticmethod
    def get_chargeback_fee(amount):
        return int(amount * settings.DAEMO_CHARGEBACK_FEE)
