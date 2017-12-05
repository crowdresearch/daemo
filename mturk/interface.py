import datetime
import json
from decimal import Decimal

from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.price import Price
from boto.mturk.qualification import (NumberHitsApprovedRequirement,
                                      PercentAssignmentsApprovedRequirement,
                                      Qualifications)
from boto.mturk.question import ExternalQuestion
from django.db.models import Q
from django.db import connection
from django.utils import timezone
from hashids import Hashids
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

from crowdsourcing.models import Task, TaskWorker, Rating
from csp import settings
from mturk.models import MTurkHIT, MTurkHITType, MTurkQualification, MTurkWorkerQualification
from mturk.utils import MultiLocaleRequirement, BoomerangRequirement

FLAG_Q_LOCALE = 0x1
FLAG_Q_RATE = 0x2
FLAG_Q_HITS = 0x4
FLAG_Q_BOOMERANG = 0x8
FLAG_Q_OTHER = 0x10

OP_LT = 'LessThan'
OP_LTEQ = 'LessThanOrEqualTo'
OP_GT = 'GreaterThan'
OP_GTEQ = 'GreaterThanOrEqualTo'
OP_EQ = 'EqualTo'
OP_NOT_EQ = 'NotEqualTo'
OP_E = 'Exists'
OP_DNE = 'DoesNotExist'
OP_IN = 'In'
OP_NOT_IN = 'NotIn'

WAIT_LIST_BUCKETS = [(1.80, 1.98), (1.60, 1.79), (1.40, 1.59), (1.20, 1.39), (1.0, 1.19)]

BOOMERANG_QUAL_INITIAL = 300


class MTurkProvider(object):
    description = 'This is a task authored by a requester on Daemo, a research crowdsourcing platform. ' \
                  'Mechanical Turk workers are welcome to do it'
    keywords = ['daemo']
    countries = ['US', 'CA']
    min_hits = 1000

    def __init__(self, host, aws_access_key_id, aws_secret_access_key):
        self.host = host
        self.connection = MTurkConnection(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            host=settings.MTURK_HOST
        )
        self.connection.APIVersion = "2014-08-15"
        if not self.host:
            raise ValueError("Please provide a host url")

    def get_connection(self):
        return self.connection

    @staticmethod
    def _mturk_system_qualifications(qualification):
        requirements = []
        for item in qualification.items.all():
            if item.expression['attribute'] not in ['location', 'approval_rate', 'total_tasks']:
                continue
            requirement = None
            if item.expression['attribute'] == 'location':
                op = OP_IN if item.expression['operator'] == 'in' else OP_NOT_IN
                requirement = MultiLocaleRequirement(op, [val.strip() for val in item.expression['value'] if
                                                          val is not None and val != ''])
            elif item.expression['attribute'] == 'approval_rate':
                op = OP_GT if item.expression['operator'] == 'gt' else OP_LT
                requirement = PercentAssignmentsApprovedRequirement(op, item.expression['value'])
            elif item.expression['attribute'] == 'total_tasks':
                op = OP_GT if item.expression['operator'] == 'gt' else OP_LT
                requirement = NumberHitsApprovedRequirement(op, item.expression['value'])

            requirements.append(requirement)
        return requirements

    def get_qualifications(self, project, boomerang_threshold, add_boomerang):
        requirements = []
        if project.qualification is not None:
            requirements += self._mturk_system_qualifications(project.qualification)
        boomerang_qual, success = self.create_qualification_type(owner_id=project.owner_id,
                                                                 project_id=project.group_id,
                                                                 name='Boomerang Score #{}'.format(project.group_id),
                                                                 flag=FLAG_Q_BOOMERANG,
                                                                 description='No description available')
        boomerang = None
        if boomerang_threshold <= int(settings.BOOMERANG_MIDPOINT * 100):
            for i, bucket in enumerate(WAIT_LIST_BUCKETS):
                if int(bucket[1] * 100) <= boomerang_threshold:

                    boomerang_blacklist, success = \
                        self.create_qualification_type(owner_id=project.owner_id,
                                                       name='Boomerang Waitlist #{}-{}'.format(project.group_id, len(
                                                           WAIT_LIST_BUCKETS) - i),
                                                       flag=FLAG_Q_BOOMERANG,
                                                       description='No description available',
                                                       deny=True,
                                                       project_id=project.group_id,
                                                       bucket=bucket)
                    if success and add_boomerang:
                        boomerang = BoomerangRequirement(qualification_type_id=boomerang_blacklist.type_id,
                                                         comparator=OP_DNE,
                                                         integer_value=None)
                        requirements.append(boomerang)

        else:
            boomerang = BoomerangRequirement(qualification_type_id=boomerang_qual.type_id, comparator=OP_GTEQ,
                                             integer_value=boomerang_threshold)
            if success and add_boomerang:
                requirements.append(boomerang)
        return Qualifications(requirements), boomerang_qual

    def create_hits(self, project, tasks=None, repetition=None):
        # if project.min_rating > 0:
        #     return 'NOOP'
        if not tasks:
            cursor = connection.cursor()
            # noinspection SqlResolve
            query = '''
                SELECT
                  max(id)                   id,
                  repetition,
                  group_id,
                  repetition - sum(existing_assignments) remaining_assignments,
                  min_rating
                FROM (
                       SELECT
                         t_rev.id,
                         t.group_id,
                         t.min_rating,
                         p.repetition,
                         CASE WHEN ma.id IS NULL OR ma.status IN (%(skipped)s, %(rejected)s, %(expired)s)
                           THEN 0
                         ELSE 1 END existing_assignments
                       FROM crowdsourcing_task t
                         INNER JOIN crowdsourcing_project p ON t.project_id = p.id
                         INNER JOIN crowdsourcing_task t_rev ON t_rev.group_id = t.group_id
                         LEFT OUTER JOIN mturk_mturkhit mh ON mh.task_id = t_rev.id
                         LEFT OUTER JOIN mturk_mturkassignment ma ON ma.hit_id = mh.id
                       WHERE t.project_id = (%(project_id)s) AND t_rev.exclude_at IS NULL
                       AND t_rev.deleted_at IS NULL
                ) t
                GROUP BY group_id, repetition, min_rating HAVING sum(existing_assignments) < repetition;
            '''
            cursor.execute(query, {'skipped': TaskWorker.STATUS_SKIPPED,
                                   'rejected': TaskWorker.STATUS_REJECTED,
                                   'expired': TaskWorker.STATUS_EXPIRED,
                                   'project_id': project.id})
            tasks = cursor.fetchall()

        rated_workers = Rating.objects.filter(origin_type=Rating.RATING_REQUESTER).count()
        add_boomerang = rated_workers > 0

        duration = project.timeout if project.timeout is not None else datetime.timedelta(hours=24)
        lifetime = project.deadline - timezone.now() if project.deadline is not None else datetime.timedelta(
            days=7)

        for task in tasks:
            question = self.create_external_question(task[0])
            mturk_hit = MTurkHIT.objects.filter(task_id=task[0]).first()
            qualifications, boomerang_qual = self.get_qualifications(project=project,
                                                                     boomerang_threshold=int(
                                                                         round(task[4], 2) * 100),
                                                                     add_boomerang=add_boomerang)
            qualifications_mask = 0
            if qualifications is not None:
                qualifications_mask = FLAG_Q_LOCALE + FLAG_Q_HITS + FLAG_Q_RATE + FLAG_Q_BOOMERANG
            hit_type, success = self.create_hit_type(title=project.name, description=self.description,
                                                     price=project.price,
                                                     duration=duration, keywords=self.keywords,
                                                     approval_delay=datetime.timedelta(days=2),
                                                     qual_req=qualifications,
                                                     qualifications_mask=qualifications_mask,
                                                     boomerang_threshold=int(round(task[4], 2) * 100),
                                                     owner_id=project.owner_id, boomerang_qual=boomerang_qual)
            if not success:
                return 'FAILURE'

            if mturk_hit is None:
                try:
                    hit = self.connection.create_hit(hit_type=hit_type.string_id,
                                                     max_assignments=task[3],
                                                     lifetime=lifetime,
                                                     question=question)[0]
                    self.set_notification(hit_type_id=hit.HITTypeId)
                    mturk_hit = MTurkHIT(hit_id=hit.HITId, hit_type=hit_type, task_id=task[0])
                except MTurkRequestError as e:
                    error = e.errors[0][0]
                    if error == 'AWS.MechanicalTurk.InsufficientFunds':
                        message = {
                            "type": "ERROR",
                            "detail": "Insufficient funds on your Mechanical Turk account!",
                            "code": error
                        }

                        redis_publisher = RedisPublisher(facility='bot', users=[project.owner])
                        message = RedisMessage(json.dumps(message))
                        redis_publisher.publish_message(message)
                    return 'FAILED'
            else:
                if mturk_hit.hit_type_id != hit_type.id:
                    result, success = self.change_hit_type_of_hit(hit_id=mturk_hit.hit_id,
                                                                  hit_type_id=hit_type.string_id)
                    if success:
                        mturk_hit.hit_type = hit_type
            mturk_hit.save()
        return 'SUCCESS'

    def create_hit_type(self, owner_id, title, description, price, duration, boomerang_threshold, keywords=None,
                        approval_delay=None, qual_req=None,
                        qualifications_mask=0, boomerang_qual=None):
        hit_type = MTurkHITType.objects.filter(owner_id=owner_id, name=title, description=description,
                                               price=Decimal(str(price)),
                                               duration=duration,
                                               qualifications_mask=qualifications_mask,
                                               boomerang_threshold=boomerang_threshold).first()
        if hit_type is not None:
            return hit_type, True

        reward = Price(price)
        try:
            mturk_ht = self.connection.register_hit_type(title=title, description=description, reward=reward,
                                                         duration=duration, keywords=keywords,
                                                         approval_delay=approval_delay,
                                                         qual_req=qual_req)[0]
            hit_type = MTurkHITType(owner_id=owner_id, name=title, description=description,
                                    price=Decimal(str(price)),
                                    keywords=keywords, duration=duration,
                                    qualifications_mask=qualifications_mask,
                                    boomerang_qualification=boomerang_qual,
                                    boomerang_threshold=boomerang_threshold)
            hit_type.string_id = mturk_ht.HITTypeId
            hit_type.save()
        except MTurkRequestError:
            return None, False
        return hit_type, True

    def create_external_question(self, task, frame_height=800):
        task_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
        task_id = task_hash.encode(task)
        url = self.host + '/mturk/task/?taskId=' + task_id
        question = ExternalQuestion(external_url=url, frame_height=frame_height)
        return question

    def update_max_assignments(self, task):
        task = Task.objects.get(id=task['id'])
        mturk_hit = task.mturk_hit
        if not mturk_hit:
            raise MTurkHIT.DoesNotExist("This task is not associated to any mturk hit")
        assignments_completed = task.task_workers.filter(~Q(status__in=[TaskWorker.STATUS_REJECTED,
                                                                        TaskWorker.STATUS_SKIPPED,
                                                                        TaskWorker.STATUS_EXPIRED])).count()
        remaining_assignments = task.project.repetition - assignments_completed
        if remaining_assignments > 0 and mturk_hit.num_assignments == mturk_hit.mturk_assignments. \
            filter(status=TaskWorker.STATUS_SUBMITTED).count() and \
                mturk_hit.mturk_assignments.filter(status=TaskWorker.STATUS_IN_PROGRESS).count() == 0:
            self.add_assignments(hit_id=mturk_hit.hit_id, increment=1)
            self.extend_hit(hit_id=mturk_hit.hit_id)
            mturk_hit.status = MTurkHIT.STATUS_IN_PROGRESS
            mturk_hit.num_assignments += 1
            mturk_hit.save()
        elif remaining_assignments == 0:
            self.expire_hit(hit_id=mturk_hit.hit_id)
            mturk_hit.status = MTurkHIT.STATUS_EXPIRED
            mturk_hit.save()
        elif remaining_assignments > 0 and \
                mturk_hit.status == MTurkHIT.STATUS_EXPIRED:
            self.extend_hit(hit_id=mturk_hit.hit_id)
            mturk_hit.status = MTurkHIT.STATUS_IN_PROGRESS
        return 'SUCCESS'

    def get_assignment(self, assignment_id):
        try:
            return self.connection.get_assignment(assignment_id)[0], True
        except MTurkRequestError as e:
            error = e.errors[0][0]
            if error == 'AWS.MechanicalTurk.InvalidAssignmentState':
                return assignment_id, False
            return None, False

    def set_notification(self, hit_type_id):
        self.connection.set_rest_notification(hit_type=hit_type_id,
                                              url=self.host + '/api/mturk/notification',
                                              event_types=['AssignmentReturned', 'AssignmentAbandoned',
                                                           'AssignmentAccepted', 'AssignmentSubmitted'])

    def approve_assignment(self, task_worker):
        task_worker_obj = TaskWorker.objects.get(id=task_worker['id'])
        if hasattr(task_worker_obj, 'mturk_assignments') and task_worker_obj.mturk_assignments.first() is not None:
            try:
                self.connection.approve_assignment(task_worker_obj.mturk_assignments.first().assignment_id)
            except MTurkRequestError:
                return False
        return True

    def reject_assignment(self, task_worker):
        task_worker_obj = TaskWorker.objects.get(id=task_worker['id'])
        if hasattr(task_worker_obj, 'mturk_assignments') and task_worker_obj.mturk_assignments.first() is not None:
            try:
                self.connection.reject_assignment(task_worker_obj.mturk_assignments.first().assignment_id)
            except MTurkRequestError:
                return False
        return True

    def expire_hit(self, hit_id):
        try:
            self.connection.expire_hit(hit_id)
        except MTurkRequestError:
            return False
        return True

    def disable_hit(self, hit_id):
        try:
            self.connection.disable_hit(hit_id)
        except MTurkRequestError:
            return False
        return True

    def extend_hit(self, hit_id):
        try:
            self.connection.extend_hit(hit_id=hit_id, expiration_increment=604800)  # 7 days
        except MTurkRequestError:
            return False
        return True

    def add_assignments(self, hit_id, increment=1):
        try:
            self.connection.extend_hit(hit_id=hit_id, assignments_increment=increment)
        except MTurkRequestError:
            return False
        return True

    def test_connection(self):
        try:
            return self.connection.get_account_balance()[0], True
        except MTurkRequestError as e:
            error = e.errors[0][0]
            if error == 'AWS.NotAuthorized':
                return None, False
            return None, False

    def get_account_balance(self):
        try:
            return self.connection.get_account_balance()[0]
        except MTurkRequestError:
            return None

    def create_qualification_type(self, owner_id, name, flag, description, project_id, auto_granted=False,
                                  auto_granted_value=None, deny=False, bucket=None):
        # noinspection SqlResolve
        query = '''
            SELECT * FROM (
                SELECT
                  task.target_id,
                  task.username,
                  round(task.task_w_avg::NUMERIC, 2) rating
                  --round(coalesce(task.task_w_avg, requester.requester_w_avg,
                  --  platform.platform_w_avg)::NUMERIC, 2) rating
                FROM (
                               SELECT
                                 target_id,
                                 origin_id,
                                 project_id,
                                 username,
                                 sum(weight * power((%(BOOMERANG_TASK_ALPHA)s), t.row_number))
                                 / sum(power((%(BOOMERANG_TASK_ALPHA)s), t.row_number)) task_w_avg
                               FROM (

                                      SELECT
                                        r.id,
                                        r.origin_id,
                                        p.group_id                              project_id,
                                        weight,
                                        r.target_id,
                                        -1 + row_number()
                                        OVER (PARTITION BY target_id
                                          ORDER BY tw.created_at DESC) AS row_number,
                                          u.username username

                                      FROM crowdsourcing_rating r
                                        INNER JOIN crowdsourcing_task t ON t.id = r.task_id
                                        INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                                        INNER JOIN crowdsourcing_taskworker tw ON t.id = tw.task_id
                                          AND tw.worker_id=r.target_id
                                        INNER JOIN auth_user u ON u.id = r.target_id
                                      WHERE origin_id = (%(origin_id)s) AND origin_type = (%(origin_type)s)) t
                               GROUP BY origin_id, target_id, project_id, username)
                             task WHERE task.project_id = (%(project_id)s)
            ) r
        '''
        extra_query = 'WHERE rating BETWEEN (%(lower_bound)s) AND (%(upper_bound)s);'
        params = {
            'origin_type': Rating.RATING_REQUESTER, 'origin_id': owner_id, 'project_id': project_id,
            'BOOMERANG_REQUESTER_ALPHA': settings.BOOMERANG_REQUESTER_ALPHA,
            'BOOMERANG_PLATFORM_ALPHA': settings.BOOMERANG_PLATFORM_ALPHA,
            'BOOMERANG_TASK_ALPHA': settings.BOOMERANG_TASK_ALPHA
        }
        obj_params = {'upper_bound': 300, 'lower_bound': 100}
        if deny and bucket is not None:
            query += extra_query
            params.update({'upper_bound': bucket[1], 'lower_bound': bucket[0]})
            obj_params.update({'upper_bound': bucket[1] * 100, 'lower_bound': bucket[0] * 100, 'is_blacklist': True})
        cursor = connection.cursor()
        cursor.execute(query, params=params)
        worker_ratings_raw = cursor.fetchall()
        worker_ratings = [{"worker_id": r[0], "worker_username": r[1], "rating": r[2]} for
                          r in worker_ratings_raw]

        qualification = MTurkQualification.objects.filter(owner_id=owner_id, flag=flag, name=name).first()
        assigned_workers = []
        if qualification is None:
            try:
                qualification_type = self.connection. \
                    create_qualification_type(name=name, description=description,
                                              status='Active',
                                              auto_granted=auto_granted,
                                              auto_granted_value=auto_granted_value)[0]
                qualification = MTurkQualification.objects.create(owner_id=owner_id, flag=flag, name=name,
                                                                  description=description,
                                                                  auto_granted=auto_granted,
                                                                  auto_granted_value=auto_granted_value,
                                                                  type_id=qualification_type.QualificationTypeId,
                                                                  **obj_params)
            except MTurkRequestError:
                return None, False
        else:
            assigned_workers = MTurkWorkerQualification.objects.values('worker').filter(
                qualification=qualification).values_list('worker', flat=True)

        for rating in worker_ratings:
            user_name = rating["worker_username"].split('.')
            if len(user_name) == 2 and user_name[0] == 'mturk':
                mturk_worker_id = user_name[1].upper()
                if mturk_worker_id not in assigned_workers:
                    self.assign_qualification(
                        qualification_type_id=qualification.type_id, worker_id=mturk_worker_id,
                        value=int(rating['rating'] * 100))
                defaults = {
                    'qualification': qualification,
                    'worker': mturk_worker_id,
                    'score': int(rating['rating'] * 100)
                }
                MTurkWorkerQualification.objects.update_or_create(qualification=qualification,
                                                                  worker=mturk_worker_id,
                                                                  defaults=defaults)
        return qualification, True

    def change_hit_type_of_hit(self, hit_id, hit_type_id):
        try:
            result = self.connection.change_hit_type_of_hit(hit_id=hit_id, hit_type=hit_type_id)
        except MTurkRequestError:
            return None, False
        return result, True

    def update_worker_boomerang(self, project_id, worker_id, task_avg, requester_avg):
        """
        Update boomerang for project
        Args:
            project_id:
            worker_id:
            task_avg:
            requester_avg

        Returns:
            str
        """
        hit = MTurkHIT.objects.select_related('hit_type__boomerang_qualification').filter(
            task__project__group_id=project_id).first()
        if hit is not None:
            qualification = hit.hit_type.boomerang_qualification
            worker_qual = MTurkWorkerQualification.objects.filter(qualification=qualification,
                                                                  worker=worker_id).first()
            if worker_qual is not None:
                self.update_score(worker_qual, score=int(task_avg * 100), override=True)
            else:
                MTurkWorkerQualification.objects.create(qualification=qualification, worker=worker_id,
                                                        score=int(task_avg * 100), overwritten=True)
                self.assign_qualification(qualification_type_id=qualification.type_id, worker_id=worker_id,
                                          value=int(task_avg * 100))

                # other_quals = MTurkWorkerQualification.objects.filter(~Q(qualification=qualification),
                #                                                       worker=worker_id,
                #                                                       overwritten=False)
                # for q in other_quals:
                #     self.update_score(q, score=int(requester_avg * 100))
        return 'SUCCESS'

    def update_score(self, worker_qual, score, override=False):
        if worker_qual is None:
            return False
        try:
            self.connection.update_qualification_score(worker_qual.qualification.type_id, worker_qual.worker, score)
            worker_qual.overwritten = override
            worker_qual.score = score
            worker_qual.save()
        except MTurkRequestError:
            return False
        return True

    def assign_qualification(self, qualification_type_id, worker_id,
                             value=1):
        """
        Revoke a qualification from a WorkerId
        Args:
            qualification_type_id:
            worker_id:
            value

        Returns:
            bool
        """
        try:
            self.connection.assign_qualification(qualification_type_id, worker_id,
                                                 value, send_notification=False)
            return True
        except MTurkRequestError:
            return False

    def revoke_qualification(self, qualification_type_id, worker_id):
        try:
            self.connection.revoke_qualification(qualification_type_id=qualification_type_id, subject_id=worker_id)
            return True
        except MTurkRequestError:
            return False

    def notify_workers(self, worker_ids, subject, message_text):
        try:
            self.connection.notify_workers(worker_ids, subject, message_text)
            return True
        except MTurkRequestError:
            return False
