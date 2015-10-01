from crowdsourcing import models
from rest_framework import serializers

class RequesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Requester


class RequesterRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RequesterRanking


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification
        fields = ('module', 'types', 'type', 'created_timestamp', 'last_updated')
        read_only_fields = ('module', 'types', 'created_timestamp', 'last_updated')