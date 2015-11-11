from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from crowdsourcing.models import FinancialAccount, Transaction, PayPalFlow
from crowdsourcing.serializers.payment import FinancialAccountSerializer, PayPalFlowSerializer, TransactionSerializer


class FinancialAccountViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = FinancialAccount.objects.all()
    serializer_class = FinancialAccountSerializer


class PayPalFlowViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    queryset = PayPalFlow.objects.all()
    serializer_class = PayPalFlowSerializer


class TransactionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer