from django.db import transaction
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.models import FinancialAccount, StripeCharge, StripeTransfer
from crowdsourcing.payment import Stripe
from crowdsourcing.permissions.payment import IsOwner
from crowdsourcing.serializers.payment import StripeChargeSerializer, \
    StripeTransferSerializer


class ChargeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    queryset = StripeCharge.objects.all()
    serializer_class = StripeChargeSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def list(self, request, *args, **kwargs):
        charges = []
        if request.user.stripe_customer is not None:
            charges = self.serializer_class(instance=request.user.stripe_customer.charges.all(), many=True).data

        return Response(data=charges)

    def create(self, request, *args, **kwargs):
        stripe = Stripe()
        amount = int(request.data.get('amount', 0) * 100)
        if amount < 100:
            return Response(data={"detail": "Amount must be greater than $1"}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            charge = stripe.create_charge(amount, user=request.user)
        return Response(data={"id": charge.id})


class TransferViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = StripeTransfer.objects.all()
    serializer_class = StripeTransferSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        transfers = self.serializer_class(instance=request.user.received_transfers, many=True).data
        return Response(data=transfers)
