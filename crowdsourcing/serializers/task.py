__author__ = 'elsabakiu, asmita, megha'

from crowdsourcing import models
from rest_framework import serializers

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ('module', 'statuses', 'status', 'deleted', 'created_timestamp', 'last_updated')
        read_only_fields = ('module', 'statuses', 'created_timestamp', 'last_updated')

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ('name', 'iso_code', 'last_updated')
        read_only_fields = ('last_updated')