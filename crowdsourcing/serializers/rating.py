from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer


class RatingSerializer(DynamicFieldsModelSerializer):
    alias = serializers.ReadOnlyField()
    task_count = serializers.ReadOnlyField()

    class Meta:
        model = models.Rating
        fields = ('id', 'origin', 'target', 'weight',
                  'origin_type', 'alias', 'task_count', 'task')
        read_only_fields = ('origin',)

    def create(self, **kwargs):
        rating, created = models.Rating.objects \
            .update_or_create(origin=kwargs['origin'],
                              origin_type=self.validated_data['origin_type'],
                              target=self.validated_data['target'],
                              task=self.validated_data.get('task'),
                              defaults={'weight': self.validated_data['weight']})
        return rating
