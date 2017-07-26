from rest_framework import serializers

from crowdsourcing import models
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer


class RegionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Region
        fields = '__all__'


class CountrySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Country
        fields = '__all__'


class CitySerializer(DynamicFieldsModelSerializer):
    country = CountrySerializer(fields=('id', 'name', 'code'))

    class Meta:
        model = models.City
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer(fields=('id', 'name', 'country', 'state_code'), allow_null=True, required=False)

    class Meta:
        model = models.Address
        fields = ('id', 'street', 'city', 'postal_code')


class LocationSerializer(serializers.Serializer):
    address = serializers.CharField(allow_blank=True, allow_null=True)
    city = serializers.CharField(allow_blank=True)
    country = serializers.CharField(allow_blank=True)
    country_code = serializers.CharField(allow_blank=True)
    state = serializers.CharField(allow_blank=True)
    state_code = serializers.CharField(allow_blank=True)
    postal_code = serializers.CharField(allow_blank=True)


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = '__all__'


class CreditCardSerializer(serializers.Serializer):
    number = serializers.CharField(min_length=13, max_length=19)
    exp_month = serializers.IntegerField(min_value=1, max_value=12)
    exp_year = serializers.IntegerField()
    cvv = serializers.RegexField(regex='^[0-9]{3,4}$', required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        fields = ('number', 'exp_month', 'exp_year', 'cvv', 'first_name', 'last_name')


class BankSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    routing_number = serializers.CharField()
    currency = serializers.CharField()
    country = serializers.CharField()

    class Meta:
        fields = ('account_number', 'routing_number', 'currency', 'country')
