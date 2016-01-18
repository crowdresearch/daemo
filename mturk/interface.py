from csp import settings
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price
from crowdsourcing.models import Task, TaskWorker
from mturk.models import MTurkHIT
from crowdsourcing.utils import get_model_or_none
import datetime
from hashids import Hashids
from django.db.models import Q
import re


class MTurkProvider(object):
    connection = MTurkConnection(aws_access_key_id=settings.MTURK_CLIENT_ID,
                                 aws_secret_access_key=settings.MTURK_CLIENT_SECRET, host=settings.MTURK_HOST)

    def __init__(self, host):
        self.host = host
        if not self.host:
            raise ValueError("Please provide a host url")

    def get_connection(self):
        return self.connection

    def create_hits(self, project, tasks=None, repetition=None):
        project_type = self.connection.register_hit_type(project.name + str(project.id),
                                                         project.description, project.price, 14400)[0].HITTypeId

        title = project.name
        reward = Price(project.price)

        max_assignments = repetition or project.repetition
        if tasks is None:
            tasks = Task.objects.filter(project=project)
        for task in tasks:
            question = self.create_external_question(task)
            if not MTurkHIT.objects.filter(task=task):
                hit = self.connection.create_hit(hit_type=project_type, max_assignments=max_assignments,
                                                 title=title,reward=reward, duration=datetime.timedelta(hours=4),
                                                 question=question)[0]
                mturk_hit = MTurkHIT(hit_id=hit.HITId, hit_type_id=hit.HITTypeId, task=task)
                mturk_hit.save()
        return 'SUCCESS'

    def create_external_question(self, task, frame_height=800):
        task_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.MTURK_HASH_MIN_LENGTH)
        task_id = task_hash.encode(task.id)
        print(task_hash.encode(task.id))
        url = self.host + '/mturk/task/?taskId='+task_id
        question = ExternalQuestion(external_url=url, frame_height=frame_height)
        return question

    def update_max_assignments(self, task):
        mturk_task = get_model_or_none(MTurkHIT, task_id=task.id)
        if not mturk_task:
            raise MTurkHIT.DoesNotExist("This task is not associated to any mturk hit")
        try:
            self.connection.expire_hit(hit_id=mturk_task.hit_id)
            mturk_task.is_expired = True
            mturk_task.save()
        except MTurkRequestError:
            pass
        repetition = task.project.repetition
        if repetition > 1:
            assignments_completed = task.task_workers.filter(~Q(task_status__in=[TaskWorker.STATUS_REJECTED,
                                                                                 TaskWorker.STATUS_SKIPPED])).count()
            max_assignments = repetition - assignments_completed
            if max_assignments > 0:
                return self.create_hits(task.project, [task], repetition=max_assignments)

        return []

    def get_assignment(self, assignment_id):
        try:
            return self.connection.get_assignment(assignment_id), True
        except MTurkRequestError as e:
            error = e.errors[0][0]
            if error == 'AWS.MechanicalTurk.InvalidAssignmentState':
                return assignment_id, False
            return None, False
