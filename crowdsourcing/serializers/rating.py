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
        rating, created = models.WorkerRequesterRating.objects\
            .update_or_create(origin=kwargs['origin'],
                              origin_type=self.validated_data['origin_type'],
                              target=self.validated_data['target'],
                              module=self.validated_data['module'],
                              defaults={'weight': self.validated_data['weight']})
        return rating