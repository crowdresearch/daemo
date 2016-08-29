import ast
import datetime
import hashlib
import random
import string
import trueskill
from django.contrib.auth.models import User

from crowdsourcing.models import *
from django.http import HttpResponse
from django.template.base import VariableNode
from django.utils import timezone
from django.utils.http import urlencode
from oauth2_provider.oauth2_backends import OAuthLibCore, get_oauthlib_core
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer

from crowdsourcing.crypto import to_pk
from csp import settings
from crowdsourcing.redis import RedisProvider
from rest_framework.exceptions import ValidationError
from django.template import Template


def get_pk(id_or_hash):
    try:
        project_id = int(id_or_hash)
        return project_id, False
    except:
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
        "ethnicity": ethnicity
    }
    return worker_data


def create_review_item(template_item, review_project, workers_to_match, worker, first_result, position):
    question = {
        "type": template_item.type,
        "role": TemplateItem.ROLE_DISPLAY,
        "name": template_item.name,
        "position": position,  # This may be wrong, check later.
        "template": review_project.template.id,
        "aux_attributes": template_item.aux_attributes
    }
    position += 1
    from crowdsourcing.serializers.template import TemplateItemSerializer
    template_item_serializer = TemplateItemSerializer(data=question)
    if template_item_serializer.is_valid():
        template_item_serializer.create()
    else:
        raise ValidationError(template_item_serializer.errors)
    username = workers_to_match[worker]['task_worker'].worker.username
    question = template_item.aux_attributes['question']['value']
    question_value = username + "'s response to " + question
    response = {
        "type": "text",
        "role": TemplateItem.ROLE_DISPLAY,
        "name": "First response",
        "position": position,
        "template": review_project.template.id,
        "aux_attributes": {
            "question": {
                "value": question_value,
                "data_source": None
            },
            "sub_type": "text_area",
            "pattern": {
                "type": "text",
                "specification": "none"
            },
            "pattern_input": None,
            "max_length": None,
            "min_length": None,
            "min": None,
            "max": None,
            "custom_error_message": None,
            "placeholder": first_result.result
        },
        "required": False
    }
    position += 1
    template_item_serializer = TemplateItemSerializer(data=response)
    if template_item_serializer.is_valid():
        template_item_serializer.create()
    else:
        raise ValidationError(template_item_serializer.errors)
    return position


def setup_peer_review(review_project, project, finished_workers, inter_task_review, match_group_id, batch_id):
    workers_to_match = []
    for task_worker in list(finished_workers):
        worker_trueskill, created = WorkerProjectScore.objects.get_or_create(
            project_group_id=project.group_id,
            worker=task_worker.worker
        )
        workers_to_match.append({'score': worker_trueskill, 'task_worker': task_worker})
    make_matchups(workers_to_match, project, review_project, inter_task_review, match_group_id, batch_id)


# Helper for setup_peer_review
def make_matchups(workers_to_match, project, review_project, inter_task_review, match_group_id, batch_id):
    matched_workers = []
    for index in xrange(0, len(workers_to_match)):
        if workers_to_match[index] not in matched_workers:
            if len(workers_to_match) - len(matched_workers) == 1:
                # If we have an odd number of workers, we need to recognize that one worker won't be matched properly,
                # so we need to do something special.
                is_last_worker = True
                start = 0
            else:
                is_last_worker = False
                start = index + 1
            first_worker = workers_to_match[index]
            first_score = trueskill.Rating(mu=first_worker['score'].mu,
                                           sigma=first_worker['score'].sigma)
            best_quality = 0
            second_worker = None
            is_intertask_match = None
            for j in xrange(start, len(workers_to_match)):
                if is_last_worker or workers_to_match[j] not in matched_workers:
                    # If we are on the last worker and he is not matched, one other worker will be assigned two matches
                    second_score = trueskill.Rating(mu=workers_to_match[j]['score'].mu,
                                                    sigma=workers_to_match[j]['score'].sigma)
                    quality = trueskill.quality_1vs1(first_score, second_score)
                    if quality > best_quality:
                        is_intertask_match = False
                        best_quality = quality
                        second_worker = workers_to_match[j]
            # Looks for matches with workers from previous tasks within this project.
            if inter_task_review:
                project_scores = WorkerProjectScore.objects.filter(
                    project_group_id=project.group_id)
                for project_score in project_scores:
                    past_workers = WorkerMatchScore.objects.filter(project_score=project_score)
                    for past_worker in past_workers:
                        if first_worker['task_worker'].worker.id != past_worker.worker.worker.id:
                            second_score = trueskill.Rating(mu=project_score.mu, sigma=project_score.sigma)
                            quality = trueskill.quality_1vs1(first_score, second_score)
                            if quality > best_quality:
                                is_intertask_match = True
                                best_quality = quality
                                second_worker = {
                                    'score': project_score,
                                    'task_worker': past_worker.worker
                                }

            if second_worker is not None:
                matched_workers.append(first_worker)
                if not is_intertask_match:
                    matched_workers.append(second_worker)
                create_review_task(first_worker, second_worker, review_project, match_group_id, batch_id)


# Helper for setup_peer_review
def create_review_task(first_worker, second_worker, review_project, match_group_id, batch_id):
    match = Match.objects.create(group_id=match_group_id)
    for worker in [first_worker, second_worker]:
        worker_score = worker['score']
        match_worker = WorkerMatchScore.objects.create(
            worker_id=worker['task_worker'].id,
            project_score=worker['score'],
            mu=worker_score.mu,
            sigma=worker_score.sigma)
        match_worker.save()
        match.worker_match_scores.add(match_worker)
    match.save()
    user_one = {
        'username': first_worker['task_worker'].worker.username,
        'task_worker': first_worker['task_worker'].id
    }
    user_two = {
        'username': second_worker['task_worker'].worker.username,
        'task_worker': second_worker['task_worker'].id
    }
    task_workers = []
    task_workers.append(user_one)
    task_workers.append(user_two)
    match_data = {
        'task_workers': task_workers
    }
    match_task = Task.objects.create(project=review_project, data=match_data, batch_id=batch_id)
    match_task.group_id = match_task.id
    match_task.save()


def is_final_review(tasks):
    for task in tasks:
        task_workers = task.task_workers.all()
        if task_workers is None:
            return False
        else:
            for task_worker in task_workers:
                if task_worker.status != TaskWorker.STATUS_SUBMITTED:
                    return False
    return True


def create_copy(instance):
    instance.pk = None
    instance.save()
    return instance


def get_template_string(initial_data, data):
    html_template = Template(initial_data)
    return_value = ''
    for node in html_template.nodelist:
        if isinstance(node, VariableNode):
            return_value += data.get(node.token.contents, '')
        else:
            return_value += node.token.contents
    return return_value


def get_template_tokens(initial_data):
    html_template = Template(initial_data)
    return [node.token.contents for node in html_template.nodelist if isinstance(node, VariableNode)]


def hash_task(data):
    return hashlib.sha256(repr(sorted(frozenset(data.iteritems())))).hexdigest()


def update_ts_scores(task_worker, winner):
    if task_worker.task.project.is_review:
        task_workers = task_worker.task.data['task_workers']
        first_user = User.objects.get(username=task_workers[0]['username'])
        second_user = User.objects.get(username=task_workers[1]['username'])
        if winner == first_user.username:
            win = WorkerProjectScore.objects.get(worker=first_user,
                                                        project_group_id=task_worker.task.project.parent.group_id)
            lose = WorkerProjectScore.objects.get(worker=second_user, project_group_id=task_worker.
                                                         task.project.parent.group_id)
        else:
            win = WorkerProjectScore.objects.get(worker=second_user,
                                                        project_group_id=task_worker.task.project.parent.group_id)
            lose = WorkerProjectScore.objects.get(worker=first_user, project_group_id=task_worker.
                                                         task.project.parent.group_id)
        winner_trueskill = trueskill.Rating(mu=win.mu, sigma=win.sigma)
        loser_trueskill = trueskill.Rating(mu=lose.mu, sigma=lose.sigma)
        winner_trueskill, loser_trueskill = trueskill.rate_1vs1(winner_trueskill, loser_trueskill)
        win.mu = winner_trueskill.mu
        win.sigma = winner_trueskill.sigma
        lose.mu = loser_trueskill.mu
        lose.sigma = loser_trueskill.sigma
        win.save()
        lose.save()
