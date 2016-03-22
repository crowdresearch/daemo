from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from mturk.models import MTurkAccount
from mturk.interface import MTurkProvider
from crowdsourcing.crypto import AESUtil
from csp.settings import AWS_DAEMO_KEY, SITE_HOST


class MTurkAccountSerializer(DynamicFieldsModelSerializer):
    client_id = serializers.CharField(required=True)
    client_secret = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = MTurkAccount
        fields = ('id', 'client_id', 'client_secret', 'is_valid',)
        read_only_fields = ('is_valid',)

    def create(self, **kwargs):
        provider = MTurkProvider(host=SITE_HOST, aws_access_key_id=self.validated_data['client_id'],
                                 aws_secret_access_key=self.validated_data['client_secret'])
        balance, is_valid = provider.test_connection()
        if not is_valid:
            raise ValidationError('Invalid AWS Keys')
        client_secret = AESUtil(key=AWS_DAEMO_KEY).encrypt(self.validated_data.pop('client_secret'))
        if not hasattr(kwargs.get('user'), 'mturk_account'):
            account = MTurkAccount.objects.create(user=kwargs.get('user'), client_secret=client_secret,
                                                  **self.validated_data)
            return account
        else:
            kwargs.get('user').mturk_account.client_id = self.validated_data['client_id']
            kwargs.get('user').mturk_account.client_secret = client_secret
            kwargs.get('user').mturk_account.save()
            return kwargs.get('user').mturk_account
