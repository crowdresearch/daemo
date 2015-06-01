__author__ = ['elsabakiu' , 'megha']

from crowdsourcing import models
from rest_framework import serializers

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ('module', 'statuses', 'status', 'deleted', 'created_timestamp', 'last_updated')
        read_only_fields = ('module', 'statuses', 'created_timestamp', 'last_updated')