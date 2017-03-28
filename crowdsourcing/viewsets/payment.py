from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from crowdsourcing.models import FinancialAccount
from crowdsourcing.permissions.payment import IsAccountOwner
from crowdsourcing.serializers.payment import FinancialAccountSerializer


class FinancialAccountViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = FinancialAccount.objects.filter(is_system=False)
    serializer_class = FinancialAccountSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]
