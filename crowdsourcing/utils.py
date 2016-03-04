from oauth2_provider.oauth2_backends import OAuthLibCore, get_oauthlib_core
from django.utils.http import urlencode
import ast
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from csp import settings
import string
import random
import datetime


def get_delimiter(filename, *args, **kwargs):
    delimiter_map = {'csv': ',', 'tsv': '\t'}
    delimiter = None
    extension = filename.split('.')[-1]
    if extension in delimiter_map:
        delimiter = delimiter_map[extension]
    return delimiter


def get_model_or_none(model, *args, **kwargs):
    """
        Get model object or return None, this will catch the DoesNotExist error.

        Keyword Arguments:
        model -- this is the model you want to query from
        other parameters are of variable length: e.g id=1 or username='jon.snow'

    """
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def get_next_unique_id(model, field, value):
    """
    Find next available incrementing value for a field in model.

    :param model: Model to be queried
    :param field: Model field to find value for
    :param value: Field value for which the next increment which is unique and available is to be found
    :return: the next unique increment value in model for the field considering index value from 1
    """

    condition = {}
    condition['%s__iregex' % field] = r'^%s[0-9]+$' % value
    values = model.objects.filter(**condition).values_list(field, flat=True)

    integers = map(lambda x: int(x.replace(value, '')), values)

    # complete sequence plus 1 extra if no gap exists
    all_values = range(1, len(integers) + 2)

    gap = list(set(all_values) - set(integers))[0]

    new_field_value = '%s%d' % (value, gap)

    return new_field_value


def get_time_delta(time_stamp):
    difference = timezone.now() - time_stamp
    days = difference.days
    hours = difference.seconds // 3600
    minutes = (difference.seconds // 60) % 60
    if minutes > 0 and hours == 0 and days == 0:
        minutes_calculated = str(minutes) + " minutes "
    elif minutes > 0 and (hours != 0 or days != 0):
        minutes_calculated = ""
    else:
        minutes_calculated = "1 minute "
    return "{days}{hours}{minutes}".format(days=str(days) + " day(s) " if days > 0 else "",
                                           hours=str(hours) + " hour(s) " if hours > 0 and days == 0 else "",
                                           minutes=minutes_calculated) + "ago"


class Oauth2Backend(OAuthLibCore):
    def _extract_params(self, request):
        """
        Extract parameters from the Django request object. Such parameters will then be passed to
        OAuthLib to build its own Request object. The body should be encoded using OAuthLib urlencoded
        """
        uri = self._get_escaped_full_path(request)
        http_method = request.method
        headers = {}  # self.extract_headers(request)
        body = urlencode(self.extract_body(request))  # TODO
        return uri, http_method, body, headers

    def create_token_response(self, request):
        """
        A wrapper method that calls create_token_response on `server_class` instance.
        :param request: The current django.http.HttpRequest object
        """
        uri, http_method, body, headers = self._extract_params(request)
        headers, body, status = get_oauthlib_core().server.create_token_response(uri, http_method, body,
                                                                                 headers)
        uri = headers.get("Location", None)

        return uri, headers, body, status

    def extract_body(self, request):
        """
        Extracts the POST body from the Django request object
        :param request: The current django.http.HttpRequest object
        :return: provided POST parameters
        """
        return request.data.items()


class Oauth2Utils:
    def create_client(self, request, user):
        from oauth2_provider.models import Application

        oauth2_client = Application.objects.create(user=user,
                                                   client_type=Application.CLIENT_CONFIDENTIAL,
                                                   authorization_grant_type=Application.GRANT_PASSWORD)
        return oauth2_client

    def get_token(self, request):
        oauth2_backend = Oauth2Backend()
        uri, headers, body, status = oauth2_backend.create_token_response(request)

        response_data = {}
        response_data["message"] = "OK"
        response_data.update(ast.literal_eval(body))
        return response_data, status

    def get_refresh_token(self, request):
        pass


class SmallResultSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class PayPalBackend:
    def __init__(self):
        import paypalrestsdk
        paypalrestsdk.configure({
            "mode": "sandbox",
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })
        self.paypalrestsdk = paypalrestsdk


def generate_random_id(length=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))


def get_relative_time(date_time):
    delta = datetime.timedelta(days=7)
    current = timezone.now()
    difference = current - date_time
    if difference.total_seconds() - delta.total_seconds() > 0:
        return date_time.strftime("%b") + ' ' + str(date_time.day)
    else:
        one_day = datetime.timedelta(days=1)
        if difference.total_seconds() - one_day.total_seconds() > 0:
            return date_time.strftime("%a")
        else:
            return date_time.strftime('%I:%M %p').lstrip('0')
