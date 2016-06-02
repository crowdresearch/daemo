from rest_framework import viewsets
from rest_framework.response import Response

from crowdsourcing import models
from crowdsourcing.permissions.util import IsOwnerOrReadOnly
from crowdsourcing.serializers.external_account import ExternalAccountSerializer


class ExternalAccountViewSet(viewsets.ModelViewSet):
    queryset = models.ExternalAccount.objects.all()
    serializer_class = ExternalAccountSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def list(self, request, *args, **kwargs):
        try:
            account = models.ExternalAccount.objects.all()
            account_serializer = ExternalAccountSerializer(account, many=True)
            return Response(account_serializer.data)
        except:
            return Response([])
