from crowdsourcing import models
from rest_framework import serializers

class WorkerRequesterRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkerRequesterRating