from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from crowdsourcing.models import FinancialAccount, Transaction, PayPalFlow, UserProfile
from crowdsourcing.serializers.payment import FinancialAccountSerializer, PayPalFlowSerializer, \
    TransactionSerializer, PayPalBalanceSerializer
from crowdsourcing.permissions.payment import IsAccountOwner
from crowdsourcing.utils import get_model_or_none


class FinancialAccountViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = FinancialAccount.objects.filter(is_system=False)
    serializer_class = FinancialAccountSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]


class PayPalFlowViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    queryset = PayPalFlow.objects.all()
    serializer_class = PayPalFlowSerializer

    def create(self, request, *args, **kwargs):
        # recipient_profile = get_model_or_none(UserProfile, user__username=recipient)
        # serializer = PayPalFlowSerializer(data=request.data, context={'request': request})
        serializer = PayPalBalanceSerializer(data=request.data)

        if serializer.is_valid():
            if serializer.validated_data['type'] == 'self':
                serializer.create_for_self(request, *args, **kwargs)
            # serializer.create(recipient=recipient_profile)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'], permission_classes=[IsAuthenticated, ])
    def create_for_self(self, request, *args, **kwargs):
        return


class TransactionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
