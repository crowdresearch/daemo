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
    country = CountrySerializer(fields=('id', 'name'))

    class Meta:
        model = models.City


class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer(fields=('id', 'name', 'country', 'state_code'), allow_null=True, required=False)

    class Meta:
        model = models.Address
        fields = ('id', 'street', 'city')


class LocationSerializer(serializers.Serializer):
    address = serializers.CharField(allow_blank=True)
    city = serializers.CharField(allow_blank=True)
    country = serializers.CharField(allow_blank=True)
    country_code = serializers.CharField(allow_blank=True)
    state = serializers.CharField(allow_blank=True)
    state_code = serializers.CharField(allow_blank=True)


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
