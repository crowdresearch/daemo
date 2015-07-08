__author__ = 'elsabakiu, asmita, megha,kajal'

from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.worker import TaskWorkerSerializer

class TaskSerializer(serializers.ModelSerializer):
  deleted = serializers.BooleanField(read_only=True)
  statuses = ((1, "Created"),(2, 'Accepted'),(3, 'Reviewed'),(4, 'Finished'))
  status=serializers.ChoiceField(choices=statuses,default=1)
  created_timestamp = serializers.DateTimeField(read_only=True)
  taskworkers = TaskWorkerSerializer(many=True)


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
    fields = ('module','status', 'deleted', 'created_timestamp', 'last_updated', 'taskworkers')
    read_only_fields = ('created_timestamp', 'last_updated')

  def create(self, **kwargs):
    task = models.Task.objects.create(**self.validated_data)
    return task


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ('name', 'iso_code', 'last_updated')
        read_only_fields = ('last_updated')