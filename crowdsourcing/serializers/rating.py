from crowdsourcing import models
from crowdsourcing.serializers.user import UserProfileSerializer
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer



class WorkerRequesterRatingSerializer(DynamicFieldsModelSerializer):
    alias = serializers.ReadOnlyField()
    task_count = serializers.ReadOnlyField()

    class Meta:
        model = models.WorkerRequesterRating
        fields = ('id', 'origin', 'target', 'module', 'weight',
                  'origin_type', 'alias', 'task_count')
        read_only_fields = ('origin', )

    def create(self, **kwargs):
        rating = models.WorkerRequesterRating.objects.create(origin=kwargs['origin'], **self.validated_data)
        return rating