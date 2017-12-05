import ast
import datetime
import hashlib
import random
import re
import string

from django.conf import settings
from django.http import HttpResponse
from django.template import Template
from django.template.base import VariableNode
from django.utils import timezone
from django.utils.http import urlencode
from oauth2_provider.oauth2_backends import OAuthLibCore, get_oauthlib_core
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.renderers import JSONRenderer

from crowdsourcing.crypto import to_pk
from crowdsourcing.redis import RedisProvider


class SmallResultsSetPagination(LimitOffsetPagination):
    default_limit = 100


def is_discount_eligible(user):
    if user.email[-4:] in settings.NON_PROFIT_EMAILS:
        return True
    return False


def get_pk(id_or_hash):
    try:
        project_id = int(id_or_hash)
        return project_id, False
    except Exception:
        return to_pk(id_or_hash), True


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
    if time_stamp is None:
        return ""

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
                                                   client_type=Application.CLIENT_PUBLIC,
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


def get_worker_cache(worker_id):
    provider = RedisProvider()
    name = provider.build_key('worker', worker_id)
    worker_stats = provider.hgetall(name)
    worker_groups = provider.smembers(name + ':worker_groups')
    approved = int(worker_stats.get('approved', 0))
    rejected = int(worker_stats.get('rejected', 0))
    submitted = int(worker_stats.get('submitted', 0))
    gender = worker_stats.get('gender')
    birthday_year = worker_stats.get('birthday_year')
    ethnicity = worker_stats.get('ethnicity')
    is_worker = worker_stats.get('is_worker', 0)
    is_requester = worker_stats.get('is_requester', 0)

    approval_rate = None
    if approved + rejected > 0:
        approval_rate = float(approved) / float(approved + rejected)

    worker_data = {
        "country": worker_stats.get('country', None),
        "approval_rate": approval_rate,
        "total_tasks": approved + rejected + submitted,
        "approved_tasks": approved,
        "worker_groups": list(worker_groups),
        "gender": gender,
        "birthday_year": birthday_year,
        "ethnicity": ethnicity,
        "is_worker": is_worker,
        "is_requester": is_requester
    }
    return worker_data


def create_copy(instance):
    instance.pk = None
    instance.save()
    return instance


def get_review_redis_message(match_group_id, project_key):
    message = {
        "type": "REVIEW",
        "payload": {
            "match_group_id": match_group_id,
            'project_key': project_key,
            "is_done": True
        }
    }
    return message


def replace_braces(s):
    return re.sub(r'\s(?=[^\{\}]*}})', '', unicode(s))


def get_template_string(initial_data, data):
    initial_data = replace_braces(initial_data)
    html_template = Template(initial_data)
    return_value = ''
    has_variables = False
    for node in html_template.nodelist:
        if isinstance(node, VariableNode):
            return_value += unicode(data.get(node.token.contents, ''))
            has_variables = True
        else:
            return_value += unicode(node.token.contents)
    return return_value, has_variables


def get_template_tokens(initial_data):
    initial_data = replace_braces(initial_data)
    html_template = Template(initial_data)
    return [node.token.contents for node in html_template.nodelist if isinstance(node, VariableNode)]


def flatten_dict(d, separator='_', prefix=''):
    return {prefix + separator + k if prefix else k: v
            for kk, vv in d.items()
            for k, v in flatten_dict(vv, separator, kk).items()
            } if isinstance(d, dict) else {prefix: d}


def hash_task(data):
    return hashlib.sha256(repr(sorted(frozenset(flatten_dict(data))))).hexdigest()


def hash_as_set(data):
    return hashlib.sha256(repr(sorted(frozenset(data)))).hexdigest()


def get_trailing_number(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else None
