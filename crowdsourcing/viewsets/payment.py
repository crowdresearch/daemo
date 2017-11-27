from django.db import transaction
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets, serializers
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.models import StripeCharge, StripeTransfer, UserProfile, TaskWorker
from crowdsourcing.payment import Stripe
from crowdsourcing.exceptions import daemo_error
from crowdsourcing.validators.project import validate_account_balance
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

    @list_route(methods=['post'], url_path='bonus')
    def bonus(self, request, *args, **kwargs):
        worker_handle = request.data.get('handle')
        amount = request.data.get('amount')
        if amount is None:
            raise serializers.ValidationError(detail=daemo_error("Enter a valid amount."))
        reason = request.data.get('reason')
        workers = UserProfile.objects.filter(handle=worker_handle)
        if workers.count() > 1:
            raise serializers.ValidationError(detail=daemo_error("Handle is not unique."))
        if workers.first() is None:
            raise serializers.ValidationError(detail=daemo_error("User not found."))
        worker = workers.first()
        if worker.user_id == request.user.id:
            raise serializers.ValidationError(detail=daemo_error("Cannot bonus self."))

        if TaskWorker.objects.filter(
            status__in=[TaskWorker.STATUS_ACCEPTED, TaskWorker.STATUS_SUBMITTED, TaskWorker.STATUS_RETURNED],
            task__project__owner=request.user, worker=worker.user
        ).count() < 1 or not hasattr(worker.user, 'stripe_account'):
            raise serializers.ValidationError(detail=daemo_error("You cannot bonus a worker "
                                                                 "who hasn't done work for you."))
        with transaction.atomic():
            validate_account_balance(request, int(amount * 100))
            stripe = Stripe()
            bonus = stripe.pay_bonus(worker=worker.user, user=request.user, amount=amount, reason=reason)
        if bonus is None:
            return Response({"message": "Bonus not created!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Bonus created successfully."})
