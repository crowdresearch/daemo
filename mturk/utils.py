import string

from boto.mturk.qualification import Requirement, LocaleRequirement
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from crowdsourcing.models import UserProfile, TaskWorker, Task
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


def is_allowed_to_work(worker, task_id, assignment_id):
    task = Task.objects.prefetch_related('project').get(id=task_id)
    task_worker = TaskWorker.objects.filter(worker=worker, task__group_id=task.group_id).first()

    if 'task_workers' in task.data:
        match_workers = [w['username'] for w in task.data['task_workers']]
        if worker.username in match_workers:
            return False

    if task_worker is None:
        return True

    if task_worker.mturk_assignments.first().assignment_id == assignment_id:
        return True
    return False


class BoomerangRequirement(Requirement):
    """
    Specifies the Boomerang Qualification Requirement
    """

    def __init__(self, qualification_type_id, comparator, integer_value, required_to_preview=False):
        super(BoomerangRequirement, self).__init__(qualification_type_id=qualification_type_id,
                                                   comparator=comparator, integer_value=integer_value,
                                                   required_to_preview=required_to_preview)


class MultiLocaleRequirement(LocaleRequirement):
    def __init__(self, comparator, locale, required_to_preview=False):
        super(MultiLocaleRequirement, self).__init__(comparator=comparator, locale=locale,
                                                     required_to_preview=required_to_preview)

    def get_as_params(self):
        params = {
            "QualificationTypeId": self.qualification_type_id,
            "Comparator": self.comparator
        }
        locales = {}
        if isinstance(self.locale, list):
            for index, country in enumerate(self.locale):
                locales['LocaleValue.%s.Country' % (index + 1)] = country
        params.update(locales)
        return params
