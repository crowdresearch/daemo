from crowdsourcing import models
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer


class WebHookSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.WebHook
        fields = ('id', 'payload', 'retry_count', 'url', 'event', 'filters',
                  'name', 'object', 'content_type', 'secret')

    def create(self, validated_data, owner=None):
        hook = self.Meta.model.objects.create(owner=owner, **validated_data)
        return hook
