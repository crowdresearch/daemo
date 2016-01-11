from rest_framework import viewsets
from rest_framework.response import Response

from crowdsourcing.serializers.accountModel import *
from crowdsourcing.models import *
from crowdsourcing.permissions.util import *


class AccountModelViewSet(viewsets.ModelViewSet):
    queryset = AccountModel.objects.all()
    serializer_class = AccountModelSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def list(self, request, *args, **kwargs):
        try:
            account = AccountModel.objects.all()
            account_serializer = AccountModelSerializer(account, many=True)
            return Response(account_serializer.data)
        except:
            return Response([])
