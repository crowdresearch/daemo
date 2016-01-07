from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import status

from crowdsourcing.models import Transaction, FinancialAccount, PayPalFlow, UserProfile
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.validators.utils import InequalityValidator, ConditionallyRequiredValidator
from crowdsourcing.utils import PayPalBackend, get_model_or_none


class FinancialAccountSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FinancialAccount
        fields = ('id', 'owner', 'type', 'is_active', 'balance')


class TransactionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'sender_type', 'amount', 'currency', 'state', 'method',
                  'sender', 'recipient', 'reference', 'created_timestamp', 'last_updated')
        read_only_fields = ('created_timestamp', 'last_updated')

    def create(self, *args, **kwargs):
        transaction = Transaction.objects.create(**self.validated_data)
        transaction.recipient.balance += transaction.amount
        transaction.recipient.save()
        if transaction.sender.type not in ['paypal_external', 'paypal_deposit']:
            transaction.sender.balance -= transaction.amount
            transaction.sender.save()
        return transaction


class PayPalFlowSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = PayPalFlow
        fields = ('id', 'paypal_id', 'state', 'recipient', 'redirect_url', 'payer_id')
        read_only_fields = ('state', 'recipient')

    def create(self, *args, **kwargs):
        flow = PayPalFlow.objects.create(
            state='created',
            recipient=kwargs['recipient'],
            paypal_id=self.validated_data['paypal_id'],
            redirect_url=self.validated_data['redirect_url']
        )

        return flow

    def execute(self, *args, **kwargs):
        paypalbackend = PayPalBackend()
        payment = paypalbackend.paypalrestsdk.Payment.find(self.validated_data['paypal_id'])
        if payment['state'] == 'approved' and not Transaction.objects.filter(reference=payment["id"]):
            return self.create_transaction(payment, self.validated_data['payer_id'])

        if payment.execute({"payer_id": self.validated_data['payer_id']}):
            return self.create_transaction(payment, self.validated_data['payer_id'])
        else:
            if Transaction.objects.filter(reference=payment["id"]):
                return payment.error['message'], status.HTTP_400_BAD_REQUEST
            else:
                return self.create_transaction(payment, self.validated_data['payer_id'])

    def create_transaction(self, payment, payer_id):
        flow = PayPalFlow.objects.get(paypal_id=payment['id'])
        flow.state = 'approved'
        flow.payer_id = payer_id
        flow.save()

        sender = FinancialAccount.objects.filter(is_system=True, type="paypal_deposit").first()

        transaction = {
            "amount": payment["transactions"][0]["amount"]["total"],
            "currency": payment["transactions"][0]["amount"]["currency"],
            "recipient": flow.recipient.id,
            "reference": payment["id"],
            "state": "approved",
            "method": payment["payer"]["payment_method"],
            "sender": sender.id
        }

        if not self.context['request'].user.is_anonymous():
            transaction["sender_type"] = "self"
        else:
            transaction["sender_type"] = "other"

        serializer = TransactionSerializer(data=transaction)

        if serializer.is_valid():
            serializer.create()
            return 'Payment executed successfully', status.HTTP_201_CREATED

        return serializer.errors, status.HTTP_400_BAD_REQUEST


class CreditCardSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['visa', 'mastercard', 'discover', 'american_express'])
    number = serializers.CharField(min_length=13, max_length=19)
    expire_month = serializers.IntegerField(min_value=1, max_value=12)
    expire_year = serializers.IntegerField()
    cvv2 = serializers.RegexField(regex='^[0-9]{3,4}$', required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        fields = ('type', 'number', 'expire_month', 'expire_year', 'cvv2', 'first_name', 'last_name')


class PayPalPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=19, decimal_places=4)
    type = serializers.ChoiceField(choices=['self', 'other'])
    username = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username', allow_null=True,
                                            required=False)
    method = serializers.ChoiceField(choices=['paypal', 'credit_card'])
    credit_card = CreditCardSerializer(many=False, required=False)

    class Meta:
        validators = [
            InequalityValidator(
                field='amount', operator='gt', value=0
            ),
            ConditionallyRequiredValidator(field='method', field2='credit_card', value='credit_card')
        ]

    def build_payment(self, *args, **kwargs):
        host = ''
        if self.context['request'].is_secure():
            host = 'https://'
        else:
            host = 'http://'
        host += self.context['request'].META['HTTP_HOST']

        payment = {"intent": "sale",
                   "payer": {
                       "payment_method": self.validated_data['method']
                   },
                   "redirect_urls": {
                       "return_url": host + "/payment-success",
                       "cancel_url": host + "/payment-cancelled"
                   },
                   "transactions": [{
                       "item_list": {
                           "items": [{
                               "name": "Daemo Deposit",
                               "sku": "DMO-7CA000",
                               "price": str(self.validated_data['amount']),
                               "currency": "USD",
                               "quantity": 1}]},
                       "amount": {
                           "total": str(self.validated_data['amount']),
                           "currency": "USD"},
                       "description": "Daemo Deposit"}]
                   }

        if self.validated_data['method'] == 'credit_card':
            payment['payer']['funding_instruments'] = [{
                "credit_card": self.validated_data['credit_card']
            }]

        return payment

    def create(self, *args, **kwargs):
        recipient = None
        recipient_profile = None

        payment_data = self.build_payment()
        if self.validated_data['type'] == 'self':
            recipient_profile = self.context['request'].user.userprofile
        else:
            recipient_profile = get_model_or_none(UserProfile, user__username=self.validated_data['username'])
        recipient = get_model_or_none(FinancialAccount, owner=recipient_profile, type='requester')
        paypalbackend = PayPalBackend()
        payment = paypalbackend.paypalrestsdk.Payment(payment_data)
        if payment.create():
            redirect_url = next((link for link in payment['links'] if link['method'] == 'REDIRECT'), '#')
            if payment['payer']['payment_method'] == 'credit_card':
                redirect_url = {
                    'href': '#'
                }
            flow_data = {
                "redirect_url": redirect_url['href'],
                "paypal_id": payment.id
            }
            payment_flow = PayPalFlowSerializer(data=flow_data, fields=('redirect_url', 'paypal_id',),
                                                context={'request': self.context['request']})
            if payment_flow.is_valid():
                payment_flow.create(recipient=recipient)
                if payment['payer']['payment_method'] == 'credit_card':
                    data = {
                        "paypal_id": payment['id'],
                        "payer_id": "UNKNOWN_CC"
                    }
                    execute_serializer = PayPalFlowSerializer(fields=('paypal_id', 'payer_id'), data=data,
                                                              context={"request": self.context['request']})
                    if execute_serializer.is_valid():
                        message, https_status = execute_serializer.execute()
                        return {"message": message}, https_status
                    else:
                        return execute_serializer.errors, status.HTTP_400_BAD_REQUEST
                return payment_flow.data, status.HTTP_201_CREATED
            else:
                return payment_flow.errors, status.HTTP_400_BAD_REQUEST
        else:
            return payment.error, status.HTTP_400_BAD_REQUEST
