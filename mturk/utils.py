import string

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from crowdsourcing.models import UserProfile
from crowdsourcing.utils import generate_random_id, get_model_or_none


def get_or_create_worker(worker_id):
    if worker_id is None:
        return None
    daemo_username = 'mturk.' + string.lower(worker_id)
    user = get_model_or_none(User, username=daemo_username)
    if user is None:
        user_obj = User.objects.create(username=daemo_username, email=daemo_username + '@daemo.stanford.edu',
                                       password=make_password(generate_random_id()), is_active=False)
        UserProfile.objects.create(user=user_obj)
        return user_obj
    else:
        return user
