from datetime import datetime

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from crowdsourcing import constants
from crowdsourcing import models
from crowdsourcing.exceptions import daemo_error
from crowdsourcing.payment import Stripe
from crowdsourcing.permissions.user import CanCreateAccount
from crowdsourcing.redis import RedisProvider
from crowdsourcing.serializers.user import UserProfileSerializer, UserSerializer, UserPreferencesSerializer
from crowdsourcing.serializers.utils import CountrySerializer, CitySerializer
from crowdsourcing.tasks import update_worker_cache
from crowdsourcing.utils import get_model_or_none


class UserViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
        This class handles user view sets
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_value_regex = '[^/]+'
    lookup_field = 'username'
    permission_classes = [CanCreateAccount]

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(validate_non_fields=True, data=request.data, context={'request': request})
        if serializer.is_valid():
            with transaction.atomic():
                serializer.create()
            return Response(serializer.data)
        raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['post'], permission_classes=[IsAdminUser, ])
    def hard_create(self, request):
        return self.create(request)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated, ])
    def change_password(self, request, username=None):
        user = request.user
        serializer = UserSerializer(validate_non_fields=True, instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.change_password()
            return Response({"message": "Password updated successfully."}, status.HTTP_200_OK)
        raise serializers.ValidationError(detail=serializer.errors)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def change_username(self, request, username=None):
        user = request.user
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.change_username()
            return Response({"message": "Username updated successfully."})
        raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['post'])
    def authenticate(self, request):
        serializer = UserSerializer()
        response_data, status = serializer.authenticate(request)
        return Response(response_data, status)

    def retrieve(self, request, username=None, *args, **kwargs):
        user = get_object_or_404(self.queryset, username=username)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)

    @list_route(methods=['post'])
    def activate_account(self, request):
        """
            this handles the account activation after the user follows the link from his/her email.
        """
        from django.contrib.auth.models import User

        try:
            activation_key = request.data.get('activation_key', None)
            activate_user = models.UserRegistration.objects.get(activation_key=activation_key)
            if activate_user:
                user = User.objects.get(id=activate_user.user_id)
                user.is_active = 1
                user.save()
                activate_user.delete()
                return Response(data={"message": "Account activated successfully"}, status=status.HTTP_200_OK)
        except models.UserRegistration.DoesNotExist:
            raise serializers.ValidationError(
                detail=daemo_error("Your account couldn't be activated. It may already be active."))

    @list_route(methods=['post'])
    def forgot_password(self, request):
        email = request.data.get('email', '')
        user = get_object_or_404(User, email=email)
        serializer = UserSerializer(context={'request': request})
        serializer.send_forgot_password(user=user)
        return Response(data={
            'message': 'Email sent.'
        }, status=status.HTTP_201_CREATED)

    @list_route(methods=['post'])
    def reset_password(self, request):
        password = request.data.get('password', 'N')
        password_reset_model = get_model_or_none(models.UserPasswordReset, reset_key=request.data.get('reset_key', ''))
        serializer = UserSerializer(context={'request': request})
        data, http_status = serializer.reset_password(reset_model=password_reset_model, password=password)
        return Response(data=data, status=http_status)

    @list_route(methods=['post'])
    def ignore_password_reset(self, request):
        password_reset_model = get_object_or_404(models.UserPasswordReset, reset_key=request.data.get('reset_key', ''))
        serializer = UserSerializer(context={'request': request})
        data, http_status = serializer.ignore_reset_password(reset_model=password_reset_model)
        return Response(data=data, status=http_status)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated], url_path='list-username')
    def list_username(self, request, *args, **kwargs):
        pattern = request.query_params.get('pattern', '$')
        user_names = self.queryset.exclude(username=request.user.username) \
            .filter(~Q(username__startswith='mock'), is_active=True, username__contains=pattern)
        serializer = UserSerializer(instance=user_names, many=True, fields=('id', 'username'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['post'], permission_classes=[IsAuthenticated, ])
    def online(self, request, *args, **kwargs):
        user = request.user
        provider = RedisProvider()
        provider.set_hash('online', user.id, datetime.utcnow())

        # online_users = provider.get_hkeys('online')

        # redis_publisher = RedisPublisher(facility='inbox', users=map(int, online_users))
        # message = RedisMessage(json.dumps({'event': 'status', 'user': user.username, 'status': 'online'}))
        # redis_publisher.publish_message(message)

        return Response(data={"message": "Success"}, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
        This class handles user profile rendering, changes and so on.
    """
    serializer_class = UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_value_regex = '[^/]+'
    lookup_field = 'user__username'

    def create(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create()
            return Response(serializer.validated_data)
        raise serializers.ValidationError(detail=serializer.errors)

    @detail_route(methods=['post'])
    def update(self, request, user__username=None, *args, **kwargs):
        serializer = UserProfileSerializer(instance=self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update()
            return Response({'status': 'updated profile'})
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @list_route()
    def get_profile(self, request):
        user_profiles = models.UserProfile.objects.all()
        serializer = UserProfileSerializer(user_profiles)
        return Response(serializer.data)

    def retrieve(self, request, user__username=None, *args, **kwargs):
        profile = get_object_or_404(self.queryset, user=request.user)
        serializer = self.serializer_class(instance=profile)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='is-complete')
    def is_complete(self, request, *args, **kwargs):
        profile = get_object_or_404(self.queryset, user=request.user)
        default_unspecified = {
            'education': False,
            'ethnicity': False,
            'gender': False,
            'birthday': False
        }
        unspecified_responses = profile.unspecified_responses or default_unspecified
        birthday = profile.birthday is not None or unspecified_responses.get('birthday', False)
        ethnicity = profile.ethnicity is not None or unspecified_responses.get('ethnicity', False)
        education = profile.education is not None or unspecified_responses.get('education', False)
        gender = profile.gender is not None or unspecified_responses.get('gender', False)
        purpose_of_use = profile.purpose_of_use is not None
        response_data = {
            'is_complete': birthday and ethnicity and education and gender and purpose_of_use,
            'fields': [{'birthday': birthday}, {'ethnicity': ethnicity}, {'education': education}, {'gender': gender},
                       {'purpose_of_use': purpose_of_use}]
        }
        return Response(data=response_data, status=status.HTTP_200_OK)

    @list_route(methods=['post'], url_path='stripe')
    def stripe(self, request, *args, **kwargs):
        from crowdsourcing.serializers.utils import CreditCardSerializer, BankSerializer
        from crowdsourcing.payment import Stripe
        is_worker = request.data.get('is_worker', False)
        is_requester = request.data.get('is_requester', False)
        ssn_last_4 = request.data.get('ssn_last_4')
        bank_data = None
        credit_card = None
        if not is_worker and not is_requester:
            raise serializers.ValidationError(detail=daemo_error("Please set either worker or requester to true."))

        if is_requester:
            card_serializer = CreditCardSerializer(data=request.data.get('credit_card', {}))
            if not card_serializer.is_valid():
                raise serializers.ValidationError(detail=card_serializer.errors)
            credit_card = request.data.get('credit_card')
        if is_worker:
            # TODO add support for other countries
            bank_data = request.data.get('bank', {})
            bank_data.update({'currency': 'usd'})
            bank_data.update({'country': 'US'})
            bank_serializer = BankSerializer(data=bank_data)
            if not bank_serializer.is_valid():
                raise serializers.ValidationError(detail=bank_serializer.errors)
        profile = request.user.profile
        account, customer = Stripe().create_account_and_customer(user=request.user,
                                                                 country_iso=profile.address.city.country.code,
                                                                 ip_address='8.8.8.8',
                                                                 is_worker=is_worker, is_requester=is_requester,
                                                                 credit_card=credit_card, bank=bank_data,
                                                                 ssn_last_4=ssn_last_4)
        if account is not None:
            profile.is_worker = True
            update_worker_cache([profile.user_id], constants.ACTION_UPDATE_PROFILE, 'is_worker', 1)

        if customer is not None:
            profile.is_requester = True
            update_worker_cache([profile.user_id], constants.ACTION_UPDATE_PROFILE, 'is_requester', 1)

        if account is not None or customer is not None:
            profile.save()
            return Response(data={"message": "Accounts and customer created"}, status=status.HTTP_201_CREATED)
        raise serializers.ValidationError(detail=daemo_error("No accounts were created, something went wrong!"))

    @list_route(methods=['get'], permission_classes=[IsAuthenticated, ], url_path='financial')
    def financial_data(self, request):
        profile = request.user.profile
        response_data = {
            "is_worker": profile.is_worker,
            "is_requester": profile.is_requester,
        }
        if hasattr(request.user, 'stripe_customer') and request.user.stripe_customer is not None:
            response_data.update({"account_balance": round(request.user.stripe_customer.account_balance, 2) / 100})
            response_data.update({"held_for_liability": 0})
            response_data.update({"default_card": request.user.stripe_customer.stripe_data.get('default_card')})
        if hasattr(request.user, 'stripe_account') and request.user.stripe_account is not None:
            response_data.update({"default_bank": request.user.stripe_account.stripe_data.get('default_bank')})

        return Response(response_data, status.HTTP_200_OK)

    @list_route(methods=['put'], permission_classes=[IsAuthenticated, ], url_path='default-credit-card')
    def update_credit_card(self, request, *args, **kwargs):
        stripe = Stripe()
        with transaction.atomic():
            stripe.update_customer_source(credit_card=request.data, user=request.user)
        return Response({"message": "Card updated successfully"}, status.HTTP_200_OK)

    @list_route(methods=['put'], permission_classes=[IsAuthenticated, ], url_path='default-bank')
    def update_bank_info(self, request, *args, **kwargs):
        bank_data = request.data
        bank_data.update({'currency': 'usd'})
        bank_data.update({'country': 'US'})
        stripe = Stripe()
        with transaction.atomic():
            stripe.update_external_account(bank=bank_data, user=request.user)
        return Response({"message": "Bank information updated successfully"}, status.HTTP_200_OK)


class UserPreferencesViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserPreferencesSerializer
    queryset = models.UserPreferences.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_value_regex = '[^/]+'
    lookup_field = 'user__username'

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(self.queryset, user=request.user)
        serializer = UserPreferencesSerializer(instance=user)
        return Response(serializer.data)

    def update(self, request, user__username=None, *args, **kwargs):
        preferences, created = models.UserPreferences.objects.get_or_create(user=request.user)
        serializer = self.serializer_class(instance=preferences, data=request.data)
        if serializer.is_valid():
            serializer.update()
            return Response({'status': 'updated preferences'})
        else:
            raise serializers.ValidationError(detail=serializer.errors)


class CountryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    JSON response for returning countries
    """
    queryset = models.Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]


class CityViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    JSON response for returning cities
    """
    queryset = models.City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
