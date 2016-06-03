from rest_framework import serializers

from crowdsourcing import models
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer


class RegionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Region


class CountrySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Country


class CitySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.City


class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer(fields=('id', 'name'), allow_null=True, required=False)

    class Meta:
        model = models.Address
        fields = ('id', 'street', 'city')


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
