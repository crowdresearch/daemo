from rest_framework import serializers
from crowdsourcing.models import WorkerRequesterRating
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer


class WorkerRequesterRatingSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = WorkerRequesterRating
        fields = ('id', 'origin', 'target', 'type', 'module', 'weight', 'created_timestamp', 'last_updated')