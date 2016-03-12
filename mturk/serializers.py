from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from mturk.models import MTurkAccount
from crowdsourcing.crypto import AESUtil
from csp.settings import AWS_DAEMO_KEY


class MTurkAccountSerializer(DynamicFieldsModelSerializer):
    client_id = serializers.CharField(required=True)
    client_secret = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = MTurkAccount
        fields = ('id', 'client_id', 'client_secret', 'is_valid',)
        read_only_fields = ('is_valid',)

    def create(self, **kwargs):
        client_secret = AESUtil(key=AWS_DAEMO_KEY).encrypt(self.validated_data.pop('client_secret'))
        account, created = MTurkAccount.objects.get_or_create(user=kwargs.get('user'), client_secret=client_secret,
                                                              **self.validated_data)
        return account
