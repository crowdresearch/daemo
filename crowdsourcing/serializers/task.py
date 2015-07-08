__author__ = 'elsabakiu, asmita, megha,kajal'

from crowdsourcing import models
from rest_framework import serializers

class TaskSerializer(serializers.ModelSerializer):

    def create(self, **kwargs):
        pass

    def update(self, instance, validated_data):
        module = validated_data.pop('module')
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance

    class Meta:
        model = models.Task
        fields = ('module','status', 'deleted', 'created_timestamp', 'last_updated')
        read_only_fields = ('created_timestamp', 'last_updated', 'deleted')


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ('name', 'iso_code', 'last_updated')
        read_only_fields = ('last_updated')