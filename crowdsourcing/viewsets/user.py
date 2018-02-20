from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from crowdsourcing import constants
from crowdsourcing import models
from crowdsourcing.exceptions import daemo_error
from crowdsourcing.models import RegistrationWhitelist
from crowdsourcing.payment import Stripe
from crowdsourcing.permissions.user import CanCreateAccount
from crowdsourcing.redis import RedisProvider
from crowdsourcing.serializers.user import UserProfileSerializer, UserSerializer, UserPreferencesSerializer
from crowdsourcing.serializers.utils import CountrySerializer, CitySerializer
from crowdsourcing.tasks import update_worker_cache
from crowdsourcing.utils import get_model_or_none, is_discount_eligible


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

    @staticmethod
    def is_whitelisted(user):
        return RegistrationWhitelist.objects.filter(email=user.email).count() > 0

    @list_route(methods=['get'], permission_classes=[IsAuthenticated], url_path='is-whitelisted')
    def is_whitelisted_route(self, request, *args, **kwargs):
        return Response({"result": self.is_whitelisted(request.user)})

    @list_route(methods=['get'], permission_classes=[IsAuthenticated], url_path='available-workers')
    def available_workers(self, request, *args, **kwargs):
        workers = models.TaskWorker.objects.values('worker').filter(
            submitted_at__gt=timezone.now() - timedelta(days=settings.WORKER_ACTIVITY_DAYS)).annotate(
            Count('worker', distinct=True))
        return Response({"count": workers.count() if len(workers) else 1})

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def activity(self, request, *args, **kwargs):
        response_data = {
            "worker": False,
            "requester": False
        }
        worker_query = '''
            SELECT
              worker_id id,
              count(day_of_month) days_of_month
            FROM (
                   SELECT
                     worker_id,
                     extract(DAY FROM submitted_at) day_of_month
                   FROM crowdsourcing_taskworker
                   WHERE submitted_at > now() - INTERVAL '30 day' AND status IN (2, 3) and worker_id=%(user_id)s
                   GROUP BY worker_id, extract(DAY FROM submitted_at)
                 ) s
            GROUP BY worker_id HAVING count(day_of_month) >= 5;
        '''
        params = {
            "user_id": request.user.id
        }
        worker = User.objects.raw(worker_query, params)
        if len(list(worker)):
            response_data['worker'] = True
        requester_query = '''
            SELECT count(DISTINCT day_of_month) id
            FROM (
                   SELECT extract(DAY FROM publish_at) day_of_month
                   FROM crowdsourcing_project
                   WHERE owner_id = %(user_id)s AND publish_at > now() - INTERVAL '30 day'
                   UNION ALL
                   SELECT extract(DAY FROM approved_at) day_of_month
                   FROM crowdsourcing_taskworker tw
                     INNER JOIN crowdsourcing_task t ON tw.task_id = t.id
                     INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                   WHERE tw.status = 3 AND p.owner_id = %(user_id)s AND tw.approved_at > now() - INTERVAL '30 day') s
            HAVING count(DISTINCT day_of_month) >= 5
        '''
        requester = User.objects.raw(requester_query, params)
        if len(list(requester)):
            response_data['requester'] = True
        return Response(response_data)

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(validate_non_fields=True, data=request.data, context={'request': request})
        if serializer.is_valid():
            with transaction.atomic():
                serializer.create()
            return Response({})
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
            .filter(~Q(username__startswith='mock'), is_active=True, profile__handle__icontains=pattern,
                    profile__is_worker=True)
        serializer = UserSerializer(instance=user_names, many=True, fields=('id', 'handle'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated, ])
    def notifications(self, request, *args, **kwargs):
        count = models.TaskWorker.objects.filter(worker=request.user, status=models.TaskWorker.STATUS_RETURNED).count()
        return Response({"returned_tasks": count})

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


class UserProfileViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        This class handles user profile rendering, changes and so on.
    """
    serializer_class = UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_value_regex = '[^/]+'
    lookup_field = 'user__profile__handle'

    # def create(self, request, *args, **kwargs):
    #     serializer = UserProfileSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.create()
    #         return Response(serializer.validated_data)
    #     raise serializers.ValidationError(detail=serializer.errors)

    # @detail_route(methods=['post'])
    def update(self, request, user__username=None, *args, **kwargs):
        if 'user' in request.data and 'email' in request.data['user'] and \
                request.user.email == request.data['user']['email']:
            del request.data['user']['email']

        serializer = UserProfileSerializer(instance=request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update()
            return Response({'status': 'updated profile'})
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['put'], url_path='update-handle')
    def update_handle(self, request, *args, **kwargs):
        new_handle = request.data.get('handle', None)
        if new_handle is None:
            raise serializers.ValidationError(detail=daemo_error("Handle cannot be null."))
        if not self._is_handle_unique(request.user, new_handle):
            raise serializers.ValidationError(detail=daemo_error("Handle is taken."))
        # if request.user.username != request.user.profile.handle:
        #     raise serializers.ValidationError(detail=daemo_error("You can update the handle only once."))
        with transaction.atomic():
            profile = models.UserProfile.objects.get(user=request.user)
            profile.handle = new_handle
            profile.save()
        return Response({"status": "Screen name updated successfully!"})

    @list_route(methods=['get'], url_path='is-handle-unique')
    def is_handle_unique(self, request, *args, **kwargs):
        handle = request.query_params.get('handle', None)
        is_unique = self._is_handle_unique(request.user, handle)
        return Response({'result': is_unique})

    @staticmethod
    def _is_handle_unique(user, handle):
        return models.UserProfile.objects.filter(~Q(user=user), handle=handle).count() == 0

    def retrieve(self, request, user__username=None, *args, **kwargs):
        profile = get_object_or_404(self.queryset, user=request.user)
        serializer = self.serializer_class(instance=profile)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
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
            if not UserViewSet.is_whitelisted(request.user):
                raise serializers.ValidationError(
                    detail=daemo_error("You are not allowed to sign up as a worker at this time."))
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
        earned = models.TaskWorker.objects.prefetch_related('task__project').values(
            'task__project__price').filter(worker=request.user,
                                           is_paid=True).values_list('task__project__price', flat=True)
        awaiting_payment = models.TaskWorker.objects.prefetch_related('task__project').values(
            'task__project__price').filter(worker=request.user,
                                           is_paid=False, status=models.TaskWorker.STATUS_ACCEPTED).values_list(
            'task__project__price', flat=True)
        response_data = {
            "is_worker": profile.is_worker,
            "is_requester": profile.is_requester,
            "awaiting_payment": sum(awaiting_payment) if len(awaiting_payment) else 0,
            "total_earned": sum(earned) if len(earned) else 0,
            "is_discount_eligible": is_discount_eligible(request.user)
        }
        response_data.update({'tasks_completed': models.TaskWorker.objects.filter(worker=request.user, status__in=[
            models.TaskWorker.STATUS_ACCEPTED, models.TaskWorker.STATUS_SUBMITTED]).count()})
        if hasattr(request.user, 'stripe_customer') and request.user.stripe_customer is not None:
            response_data.update({"account_balance": round(request.user.stripe_customer.account_balance, 2) / 100})
            response_data.update({"held_for_liability": 0})

            if hasattr(request.user.stripe_customer, 'stripe_data') and \
                    request.user.stripe_customer.stripe_data is not None:
                response_data.update({"default_card": request.user.stripe_customer.stripe_data.get('default_card')})
        if hasattr(request.user, 'stripe_account') and request.user.stripe_account is not None \
            and hasattr(request.user.stripe_account, 'stripe_data') and \
                request.user.stripe_account.stripe_data is not None:
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

    @staticmethod
    def _get_projects_as_requester(worker_id, owner_id):
        query = '''
            SELECT DISTINCT
                p.group_id id,
              p.name,
              count(tw.id) tasks_completed,
              coalesce(avg(r.weight), 2.0) rating
            FROM crowdsourcing_project p
              INNER JOIN crowdsourcing_task t ON t.project_id = p.id
              INNER JOIN crowdsourcing_taskworker tw ON tw.task_id = t.id
              LEFT OUTER JOIN crowdsourcing_rating r
                ON r.task_id = t.id AND tw.worker_id = r.target_id
                AND r.origin_id = p.owner_id AND r.origin_type = %(origin_type)s
            WHERE tw.worker_id = %(worker_id)s AND p.owner_id = %(owner_id)s AND tw.status IN (2, 3)
            GROUP BY p.group_id, p.name ORDER BY p.group_id desc;
        '''
        params = {
            "worker_id": worker_id,
            "owner_id": owner_id,
            "origin_type": models.Rating.RATING_REQUESTER,
        }
        return models.Project.objects.raw(query, params=params)

    @staticmethod
    def _get_projects_as_worker(worker_id, owner_id):
        query = '''
                SELECT DISTINCT
                    p.group_id id,
                  p.name,
                  count(tw.id) tasks_completed,
                  coalesce(avg(r.weight), 2.0) rating
                FROM crowdsourcing_project p
                  INNER JOIN crowdsourcing_task t ON t.project_id = p.id
                  INNER JOIN crowdsourcing_taskworker tw ON tw.task_id = t.id
                  LEFT OUTER JOIN crowdsourcing_rating r
                    ON r.task_id = t.id AND p.owner_id = r.target_id
                    AND r.origin_id = tw.worker_id AND r.origin_type = %(origin_type)s
                WHERE tw.worker_id = %(worker_id)s AND p.owner_id = %(owner_id)s AND tw.status IN (2, 3)
                GROUP BY p.group_id, p.name ORDER BY p.group_id desc;
            '''
        params = {
            "worker_id": worker_id,
            "owner_id": owner_id,
            "origin_type": models.Rating.RATING_WORKER,
        }
        return models.Project.objects.raw(query, params=params)

    @detail_route(methods=['get'], url_path='public')
    def public(self, request, *args, **kwargs):
        profile = self.get_object()
        tasks_completed = models.TaskWorker.objects.filter(worker_id=profile.id,
                                                           status__in=[models.TaskWorker.STATUS_ACCEPTED]).count()

        my_projects = self._get_projects_as_requester(worker_id=profile.user_id, owner_id=request.user.id)
        their_projects = self._get_projects_as_worker(owner_id=profile.user_id, worker_id=request.user.id)
        own_projects = [{"id": mp.id, "name": mp.name, "tasks_completed": mp.tasks_completed, "rating": mp.rating} for
                        mp in
                        my_projects]
        projects_worked_on = [
            {"id": mp.id, "name": mp.name, "tasks_completed": mp.tasks_completed, "rating": mp.rating}
            for mp in
            their_projects]
        return Response(
            {
                "member_since": profile.user.date_joined,
                "tasks_completed": tasks_completed,
                "handle": profile.handle,
                "id": profile.user_id,
                "own_projects": own_projects,
                "is_worker": profile.is_worker and len(own_projects) > 0,
                "projects_worked_on": projects_worked_on
            }
        )


class UserPreferencesViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    serializer_class = UserPreferencesSerializer
    queryset = models.UserPreferences.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_value_regex = '[^/]+'
    lookup_field = 'user__username'

    def list(self, request, *args, **kwargs):
        user = get_object_or_404(self.queryset, user=request.user)
        serializer = UserPreferencesSerializer(instance=user)
        return Response(serializer.data)

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
