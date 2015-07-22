__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region

    def create(self, **kwargs):
        # Create region from unmodified data
        region = models.Region.objects.create(**self.initial_data)
        return region


class CountrySerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = models.Country

    def create(self, **kwargs):
        # Passing unmodified region data to RegionSerializer
        region_data = self.initial_data.pop('region')
        region_serializer = RegionSerializer(data=region_data)
        region = region_serializer.create()

        # Create country with region and unmodified data
        country = models.Country.objects.create(region=region, **self.initial_data)
        return country


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = models.City

    def create(self, **kwargs):
        # Passing unmodified country data to CountrySerializer to serialize nested objects
        country_data = self.initial_data.pop('country')
        country_serializer = CountrySerializer(data=country_data)
        country = country_serializer.create()

        # Create city with country and unmodified data
        city = models.City.objects.create(country=country, **self.initial_data)
        return city


class AddressSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    city = CitySerializer()

    class Meta:
        model = models.Address

    def create(self, **kwargs):
        # Passing unmodified country data to CountrySerializer to serialize nested objects
        country_data = self.initial_data.pop('country')
        country_serializer = CountrySerializer(data=country_data)
        country = country_serializer.create()

        # Passing unmodified city data to CitySerializer to serialize nested objects
        city_data = self.initial_data.pop('city')
        city_serializer = CitySerializer(data=city_data)
        city = city_serializer.create()

        # Create address with country, city and unmodified data
        address = models.Address.objects.create(country=country, city=city, **self.initial_data)
        return address


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
