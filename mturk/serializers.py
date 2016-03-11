from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from mturk.models import MTurkAccount


class MTurkAccountSerializer(DynamicFieldsModelSerializer):
    client_secret = serializers.CharField(write_only=True)

    class Meta:
        model = MTurkAccount
        fields = ('id', 'client_id', 'client_secret', 'is_valid',)
        read_only_fields = ('is_valid',)

    def create(self, **kwargs):
        created, account = MTurkAccount.objects.get_or_create(user=kwargs.get('user'), **self.validated_data)
        return account
