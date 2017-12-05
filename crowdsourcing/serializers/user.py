import hashlib
import random
import re
import uuid

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.validators import UniqueValidator

from crowdsourcing import constants
from crowdsourcing import models
from crowdsourcing.discourse import DiscourseClient
from crowdsourcing.emails import send_password_reset_email, send_activation_email
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.serializers.payment import FinancialAccountSerializer
from crowdsourcing.serializers.utils import AddressSerializer, CurrencySerializer, LanguageSerializer, \
    LocationSerializer
from crowdsourcing.tasks import update_worker_cache
from crowdsourcing.utils import get_model_or_none, get_next_unique_id, Oauth2Utils
from crowdsourcing.validators.utils import EqualityValidator, LengthValidator
from csp import settings


class UserSerializer(DynamicFieldsModelSerializer):
    last_login = serializers.DateTimeField(required=False, read_only=True)
    date_joined = serializers.DateTimeField(required=False, read_only=True)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    is_worker = serializers.BooleanField(required=False, write_only=True)
    is_requester = serializers.BooleanField(required=False, write_only=True)
    handle = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        validators = [
            EqualityValidator(
                fields=['password1', 'password2']
            ),
            LengthValidator('password1', 8),
        ]
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'last_login', 'date_joined', 'is_worker', 'is_requester', 'handle')

    def __init__(self, validate_non_fields=False, **kwargs):
        super(UserSerializer, self).__init__(**kwargs)
        self.validate_non_fields = validate_non_fields

    @staticmethod
    def get_handle(obj):
        return obj.profile.handle

    def validate_username(self, value):
        user = User.objects.filter(username=value)
        if user:
            raise ValidationError("Username needs to be unique.")
        return value

    def create(self, **kwargs):
        username = ''

        validated_username = self.validated_data['first_name'].lower() + '.' + self.validated_data['last_name'].lower()
        username_check = User.objects.filter(username=validated_username).count()

        if username_check == 0 and len(validated_username) <= settings.USERNAME_MAX_LENGTH:
            username = validated_username
        else:
            username = get_next_unique_id(User, 'username', validated_username)
            if len(username) > settings.USERNAME_MAX_LENGTH:
                if len(self.validated_data['email']) <= settings.USERNAME_MAX_LENGTH:
                    username = self.validated_data['email']
                else:
                    username = uuid.uuid4().hex[:settings.USERNAME_MAX_LENGTH]

        user = User.objects.create_user(username, self.validated_data.get('email'),
                                        self.initial_data.get('password1'))

        # if settings.EMAIL_ENABLED:
        user.is_active = 0
        user.first_name = self.validated_data['first_name']
        user.last_name = self.validated_data['last_name']
        user.save()

        user_profile = models.UserProfile.objects.create(user=user, is_worker=False, is_requester=False,
                                                         handle=username)
        profile_data = {
            'location': self.initial_data.get('location', {}),
            'birthday': self.initial_data.get('birthday', None),
            'user': {}
        }
        user_profile_serializer = UserProfileSerializer(instance=user_profile, data=profile_data, partial=True)

        if user_profile_serializer.is_valid():
            user_profile = user_profile_serializer.update()

        update_worker_cache([user.id], constants.ACTION_UPDATE_PROFILE, 'is_worker', 0)
        update_worker_cache([user.id], constants.ACTION_UPDATE_PROFILE, 'is_requester', 0)
        # update_worker_cache([user.id], constants.ACTION_UPDATE_PROFILE, 'birthday_year',
        #                     user_profile.birthday.year)

        models.UserPreferences.objects.create(user=user)

        # if self.validated_data.get('is_requester', True):
        #     user_profile.is_requester = True
        #     user_profile.save()
        #     requester_financial_account = models.FinancialAccount()
        #     requester_financial_account.owner = user
        #     requester_financial_account.type = models.FinancialAccount.TYPE_REQUESTER
        #     requester_financial_account.save()
        #
        # has_profile_info = self.validated_data.get('is_requester', False) or self.validated_data.get('is_worker',
        #                                                                                              False)

        # if self.validated_data.get('is_worker', True) or not has_profile_info:
        #     user_profile.is_worker = True
        #     user_profile.save()
        #     worker_financial_account = models.FinancialAccount()
        #     worker_financial_account.owner = user
        #     worker_financial_account.type = models.FinancialAccount.TYPE_WORKER
        #     worker_financial_account.save()

        if settings.EMAIL_ENABLED:
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            if isinstance(username, str):
                username = username.encode('utf-8')
            activation_key = hashlib.sha1(salt.encode('utf-8') + username).hexdigest()
            registration_model = models.UserRegistration()
            registration_model.user = User.objects.get(id=user.id)
            registration_model.activation_key = activation_key
            send_activation_email(email=user.email, host=self.context['request'].get_host(),
                                  activation_key=activation_key)
            registration_model.save()

        if settings.DISCOURSE_BASE_URL and settings.DISCOURSE_API_KEY:
            try:
                client = DiscourseClient(
                    settings.DISCOURSE_BASE_URL,
                    api_username='system',
                    api_key=settings.DISCOURSE_API_KEY)

                client.create_user(name=user.get_full_name(),
                                   username=user.profile.handle,
                                   email=user.email,
                                   password=self.initial_data.get('password1'),
                                   active=True,
                                   approved=True)
            except Exception:
                print("Failed to create Discourse user!")

        return user

    def change_password(self):
        from django.contrib.auth import authenticate as auth_authenticate

        if 'password' not in self.initial_data:
            raise ValidationError("Current password needs to be provided")
        user = auth_authenticate(username=self.instance.username, password=self.initial_data['password'])
        if user is not None:
            self.instance.set_password(self.initial_data['password1'])
            self.instance.save()
        else:
            raise ValidationError("Old password is incorrect.")

    def authenticate(self, request):
        from django.contrib.auth import authenticate as auth_authenticate

        # self.redirect_to = request.POST.get('next', '') #to be changed, POST does not contain any data

        username = request.data.get('username', '')
        password = request.data.get('password', '')

        email_or_username = username

        # match with username if not email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_or_username):
            username = email_or_username
        else:
            user = get_model_or_none(User, email=email_or_username)

            if user is not None:
                username = user.username

        user = auth_authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                oauth2_utils = Oauth2Utils()
                client = oauth2_utils.create_client(request, user)

                response_data = dict()
                response_data["client_id"] = client.client_id
                response_data["client_secret"] = client.client_secret
                response_data["username"] = user.username
                response_data["email"] = user.email
                response_data["first_name"] = user.first_name
                response_data["last_name"] = user.last_name
                response_data["date_joined"] = user.date_joined
                response_data["last_login"] = user.last_login
                response_data["is_requester"] = user.profile.is_requester
                response_data["is_worker"] = user.profile.is_worker

                return response_data, status.HTTP_201_CREATED
            else:
                raise AuthenticationFailed(_('Account is not activated yet.'))
        else:
            raise AuthenticationFailed(_('Username or password is incorrect.'))

    def change_username(self, **kwargs):
        from django.contrib.auth import authenticate as auth_authenticate

        if 'password' not in self.initial_data:
            raise ValidationError("Current password needs to be provided")
        if 'username' not in self.initial_data:
            raise ValidationError("New username needs to be provided")

        user = auth_authenticate(username=self.instance.username, password=self.initial_data['password'])

        if user is not None:
            self.instance.username = self.initial_data['username']
            self.instance.save()
        else:
            raise ValidationError("Username or password is incorrect.")

    def send_forgot_password(self, **kwargs):
        user = kwargs['user']
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        username = user.username
        reset_key = hashlib.sha1(str(salt + username).encode('utf-8')).hexdigest()
        password_reset = get_model_or_none(models.UserPasswordReset, user_id=user.id)
        if password_reset is None:
            password_reset = models.UserPasswordReset()
        password_reset.user = user
        password_reset.reset_key = reset_key
        if settings.EMAIL_ENABLED:
            password_reset.save()
            send_password_reset_email(email=user.email, host=self.context['request'].get_host(),
                                      reset_key=reset_key)

    def reset_password(self, **kwargs):
        """
            Resets the password if requested by the user.
        """
        if len(kwargs['password']) < 8:
            raise ValidationError("New password must be at least 8 characters long")
        if not kwargs['reset_model']:
            raise ValidationError("Invalid email or reset key")
        user = get_model_or_none(User, id=kwargs['reset_model'].user_id, email=self.context['request'].data
                                 .get('email', 'NO_EMAIL'))
        if not user:
            raise ValidationError("Invalid email or reset key")
        user.set_password(kwargs['password'])
        user.save()
        kwargs['reset_model'].delete()
        return {"message": "Password reset successfully"}, status.HTTP_200_OK

    @staticmethod
    def ignore_reset_password(**kwargs):
        kwargs['reset_model'].delete()
        return {"message": "Ignored"}, status.HTTP_204_NO_CONTENT


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(fields=('first_name', 'last_name', 'email'))
    user_username = serializers.ReadOnlyField(source='user.username', read_only=True)
    birthday = serializers.DateTimeField(allow_null=True)
    address = AddressSerializer(allow_null=True, required=False)
    location = LocationSerializer(allow_null=True, required=False)
    is_verified = serializers.BooleanField(read_only=True)
    financial_accounts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.UserProfile
        fields = ('user', 'user_username', 'gender', 'birthday', 'is_verified', 'address', 'nationality',
                  'picture', 'created_at', 'id', 'financial_accounts',
                  'ethnicity', 'job_title', 'income', 'education', 'location', 'unspecified_responses',
                  'purpose_of_use', 'is_worker', 'is_requester', 'handle')

    def create(self, **kwargs):
        address_data = self.validated_data.pop('address')
        address = models.Address.objects.create(**address_data)
        user_data = self.validated_data.pop('user')
        user_profile = models.UserProfile.objects.create(address=address, user=user_data.id, **self.validated_data)
        return user_profile

    def update(self, **kwargs):
        user = self.validated_data.pop('user')
        if self.validated_data.get('location') is not None:
            location_data = self.validated_data.pop('location')
            city_name = None
            country_name = None
            country_code = None
            state_name = ""
            state_code = ""
            street_name = None
            postal_code = ""

            if 'city' in location_data:
                city_name = location_data.pop('city')
            if 'postal_code' in location_data:
                postal_code = location_data.pop('postal_code')

            if 'country' in location_data:
                country_name = location_data.pop('country')
                country_code = location_data.pop('country_code')

            if 'address' in location_data:
                street_name = location_data.pop('address')

            if 'state' in location_data:
                state_name = location_data.pop('state')
                state_code = location_data.pop('state_code')

            if country_name is not None and city_name is not None:
                country, created = models.Country.objects.get_or_create(name=country_name, code=country_code)
                city, created = models.City.objects.get_or_create(name=city_name, state=state_name,
                                                                  state_code=state_code, country=country)
                address, created = models.Address.objects.get_or_create(street=street_name, city=city,
                                                                        postal_code=postal_code)
                self.instance.address = address
            else:
                self.instance.address = None

        self.instance.gender = self.validated_data.get('gender', self.instance.gender)
        self.instance.birthday = self.validated_data.get('birthday', self.instance.birthday)
        self.instance.is_verified = self.validated_data.get('is_verified', self.instance.is_verified)
        self.instance.picture = self.validated_data.get('picture', self.instance.picture)
        self.instance.ethnicity = self.validated_data.get('ethnicity', self.instance.ethnicity)
        self.instance.purpose_of_use = self.validated_data.get('purpose_of_use', self.instance.purpose_of_use)
        self.instance.unspecified_responses = self.validated_data.get('unspecified_responses',
                                                                      self.instance.unspecified_responses)
        self.instance.education = self.validated_data.get('education', self.instance.education)
        self.instance.save()
        self.instance.user.first_name = user.get('first_name', self.instance.user.first_name)
        self.instance.user.last_name = user.get('last_name', self.instance.user.last_name)
        self.instance.user.save()

        update_worker_cache([self.instance.user_id], constants.ACTION_UPDATE_PROFILE, 'gender', self.instance.gender)
        if self.instance.birthday is not None:
            update_worker_cache([self.instance.user_id], constants.ACTION_UPDATE_PROFILE, 'birthday_year',
                                self.instance.birthday.year)
        update_worker_cache([self.instance.user_id], constants.ACTION_UPDATE_PROFILE, 'ethnicity',
                            self.instance.ethnicity)

        return self.instance

    @staticmethod
    def get_financial_accounts(obj):
        serializer = FinancialAccountSerializer(instance=obj.user.financial_accounts, many=True, read_only=True,
                                                fields=('id', 'type', 'type_detail', 'is_active', 'balance'))

        return serializer.data

    @staticmethod
    def create_worker():
        pass


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = {'id', 'name'}


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserRole


class UserPreferencesSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    currency = CurrencySerializer(required=False)
    language = LanguageSerializer(required=False)
    auto_accept = serializers.BooleanField(required=False)

    class Meta:
        model = models.UserPreferences
        fields = ('user', 'language', 'currency', 'login_alerts', 'auto_accept', 'new_tasks_notifications',
                  'aux_attributes')

    def create(self, **kwargs):
        currency_data = self.validated_data.pop('currency')
        language_data = self.validated_data.pop('language')

        currency = None
        if currency_data is not None:
            currency = models.Currency.objects.create(**currency_data)

        language = None
        if language_data is not None:
            language = models.Language.objects.create(**language_data)

        user_data = self.validated_data.pop('user')
        user = User.objects.get(id=user_data.id)
        pref_objects = models.UserPreferences.objects
        user_preferences = pref_objects.create(currency=currency, language=language, user=user, **self.validated_data)
        return user_preferences

    def update(self, **kwargs):
        self.instance.auto_accept = self.validated_data.get('auto_accept', self.instance.auto_accept)
        self.instance.new_tasks_notifications = self.validated_data.get('new_tasks_notifications',
                                                                        self.instance.new_tasks_notifications)
        self.instance.save()
        return self.instance
