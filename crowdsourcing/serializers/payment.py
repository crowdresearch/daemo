from crowdsourcing.models import Transaction, FinancialAccount, PayPalFlow
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer


class FinancialAccountSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FinancialAccount
        fields = ('id', 'profile', 'type', 'id_string', 'is_active', 'balance')


class TransactionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'id_string', 'sender_type', 'amount', 'currency', 'state', 'method',
                  'sender', 'recipient', 'reference', 'created_timestamp', 'last_updated')


class PayPalFlowSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = PayPalFlow
        fields = ('id', 'paypal_id', 'sender', 'state', 'recipient')
