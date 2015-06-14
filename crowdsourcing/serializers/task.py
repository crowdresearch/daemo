__author__ = 'elsabakiu, asmita, megha,kajal'

from crowdsourcing import models
from rest_framework import serializers

class TaskSerializer(serializers.ModelSerializer):
  deleted = serializers.BooleanField(read_only=True)
  status=serializers.IntegerField()
  created_timestamp = serializers.DateTimeField(read_only=True)

  def create(self, **kwargs):
    task = models.Task.objects.create(deleted = False,**self.validated_data)
    worker = validated_data.pop('Worker')
    for t in task:
      models.TaskWorker.objects.create(task=t,worker=worker)
    return task
  
  def update(self, instance, validated_data):
    module = validated_data.pop('Module')
    instance.status = validated_data.get('status', instance.status)
    instance.statuses = validated_data.get('statuses', instance.statuses)
    instance.save()
    return instance

  def delete(self, instance):
    instance.deleted = True
    instance.save()
    return instance

class Meta:
  model = models.Task
  fields = ('module', 'statuses', 'status', 'deleted', 'created_timestamp', 'last_updated')
  read_only_fields = ('module', 'statuses', 'created_timestamp', 'last_updated')

class CurrencySerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Currency
    fields = ('name', 'iso_code', 'last_updated')
    read_only_fields = ('last_updated')