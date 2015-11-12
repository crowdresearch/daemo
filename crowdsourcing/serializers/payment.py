from crowdsourcing.models import Transaction, FinancialAccount, PayPalFlow, UserProfile
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from crowdsourcing.validators.utils import InequalityValidator, ConditionallyRequiredValidator
from crowdsourcing.utils import PayPalBackend, get_model_or_none
from rest_framework import status
from django.utils import timezone

class FinancialAccountSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FinancialAccount
        fields = ('id', 'owner', 'type', 'id_string', 'is_active', 'balance')


class TransactionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'id_string', 'sender_type', 'amount', 'currency', 'state', 'method',
                  'sender', 'recipient', 'reference', 'created_timestamp', 'last_updated')


class PayPalFlowSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = PayPalFlow
        fields = ('id', 'paypal_id', 'sender', 'state', 'recipient', 'redirect_url', 'payer_id')
        read_only_fields = ('sender', 'state', 'recipient')

    def create(self, *args, **kwargs):
        flow = PayPalFlow()
        if not self.context['request'].user.is_anonymous():
            flow.sender = self.context['request'].user.userprofile
        flow.state = 'created'
        flow.recipient = kwargs['recipient']
        flow.paypal_id = self.validated_data['paypal_id']
        flow.redirect_url = self.validated_data['redirect_url']
        flow.save()
        return flow

    def execute(self, *args, **kwargs):
        paypalbackend = PayPalBackend()
        payment = paypalbackend.paypalrestsdk.Payment.find(self.validated_data['paypal_id'])
        PayPalFlow.objects.filter(paypal_id=self.validated_data['paypal_id']).\
            update(state='approved', payer_id=self.validated_data['payer_id'], last_updated=timezone.now())
        if payment.execute({"payer_id": self.validated_data['payer_id']}):
            return "Payment executed successfully", status.HTTP_201_CREATED
        else:
            return payment.error['message'], status.HTTP_400_BAD_REQUEST


class CreditCardSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['visa', 'mastercard', 'discover', 'american_express'])
    number = serializers.CharField(min_length=13, max_length=19)
    expire_month = serializers.IntegerField(min_value=1, max_value=12)
    expire_year = serializers.IntegerField()
    cvv2 = serializers.IntegerField(min_value=111, max_value=9999)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        fields = ('type', 'number', 'expire_month', 'expire_year', 'cvv2', 'first_name', 'last_name')


class PayPalPaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    type = serializers.ChoiceField(choices=['self', 'other'])
    username = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username', allow_null=True)
    method = serializers.ChoiceField(choices=['paypal', 'credit_card'])
    credit_card = CreditCardSerializer(many=False, required=False)

    class Meta:
        validators = [
            InequalityValidator(
                field='amount', operator='gt', value=1
            ),
            ConditionallyRequiredValidator(field='method', field2='credit_card', value='credit_card')
        ]

    def build_payment(self, *args, **kwargs):
        payment = {"intent": "sale",
                   "payer": {
                       "payment_method": self.validated_data['method']
                   },
                   "redirect_urls": {
                       "return_url": "http://localhost:8000/paypal-success",
                       "cancel_url": "http://localhost:8000/paypal-cancelled"
                   },
                   "transactions": [{
                       "item_list": {
                           "items": [{
                               "name": "Daemo Deposit.",
                               "sku": "DMO-7CA000",
                               "price": self.validated_data['amount'],
                               "currency": "USD",
                               "quantity": 1}]},
                       "amount": {
                           "total": self.validated_data['amount'],
                           "currency": "USD"},
                       "description": "Daemo Deposit."}]
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
            flow_data = {
                "redirect_url": redirect_url['href'],
                "paypal_id": payment.id
            }
            payment_flow = PayPalFlowSerializer(data=flow_data, fields=('redirect_url', 'paypal_id', ),
                                                context={'request': self.context['request']})
            if payment_flow.is_valid():
                flow = payment_flow.create(recipient=recipient)
                return flow, status.HTTP_201_CREATED
            else:
                return payment_flow.errors, status.HTTP_400_BAD_REQUEST
        else:
            return payment.error
