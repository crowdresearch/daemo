from crowdsourcing.models import Transaction, FinancialAccount, PayPalFlow
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from crowdsourcing.validators.utils import InequalityValidator, ConditionallyRequiredValidator


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
        fields = ('id', 'paypal_id', 'sender', 'state', 'recipient',)
        read_only_fields = ('sender', 'sender', 'state', 'recipient',)

    def create(self, *args, **kwargs):
        flow = PayPalFlow()
        if not self.context['request'].user.anonymous():
            flow.sender = self.context['request'].user.userprofile
        flow.state = 'created'
        flow.recipient = kwargs['recipient']
        flow.paypal_id = self.validated_data['paypal_id']
        flow.save()
        return flow




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
                   "transactions": [{
                       "item_list": {
                           "items": [{
                               "name": "Daemo Deposit.",
                               "sku": "item",
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