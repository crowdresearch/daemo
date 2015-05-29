__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
import json


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
