from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins

from crowdsourcing.models import FinancialAccount, Transaction, PayPalFlow
from crowdsourcing.serializers.payment import FinancialAccountSerializer, PayPalFlowSerializer, \
    TransactionSerializer, PayPalPaymentSerializer
from crowdsourcing.permissions.payment import IsAccountOwner


class FinancialAccountViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = FinancialAccount.objects.filter(is_system=False)
    serializer_class = FinancialAccountSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]


class PayPalFlowViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    queryset = PayPalFlow.objects.all()
    serializer_class = PayPalFlowSerializer

    def create(self, request, *args, **kwargs):
        serializer = PayPalPaymentSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            flow_data, http_status = serializer.create()
            return Response(data=flow_data, status=http_status)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def execute(self, request, *args, **kwargs):
        serializer = PayPalFlowSerializer(fields=('paypal_id', 'payer_id'), data=request.data,
                                          context={"request": request})
        if serializer.is_valid():
            message, https_status = serializer.execute()
            return Response(data={"message": message}, status=https_status)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
