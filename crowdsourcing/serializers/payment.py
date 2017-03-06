from rest_framework import serializers

from crowdsourcing.models import FinancialAccount
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer


class FinancialAccountSerializer(DynamicFieldsModelSerializer):
    type_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FinancialAccount
        fields = ('id', 'owner', 'type', 'type_detail', 'is_active', 'balance')

    def get_type_detail(self, obj):
        types = dict(FinancialAccount.TYPE)
        return types[obj.type]


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
