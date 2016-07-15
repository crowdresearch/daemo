import datetime
from decimal import Decimal

from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.price import Price
from boto.mturk.qualification import (NumberHitsApprovedRequirement,
                                      PercentAssignmentsApprovedRequirement,
                                      Qualifications)
from boto.mturk.question import ExternalQuestion
from django.db.models import Q, Avg
from django.utils import timezone
from hashids import Hashids

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

BOOMERANG_QUAL_INITIAL = 300


class MTurkProvider(object):
    description = 'This is a task authored by a requester on Daemo, a research crowdsourcing platform. ' \
                  'Mechanical Turk workers are welcome to do it'
    keywords = ['daemo']
    countries = ['US', 'CA']
    min_hits = 1000

    def __init__(self, host, aws_access_key_id, aws_secret_access_key):
        self.host = host
        self.connection = MTurkConnection(aws_access_key_id=aws_access_key_id,
                                          aws_secret_access_key=aws_secret_access_key, host=settings.MTURK_HOST)
        self.connection.APIVersion = "2014-08-15"
        if not self.host:
            raise ValueError("Please provide a host url")

    def get_connection(self):
        return self.connection

    def get_qualifications(self, owner_id, boomerang_threshold, project_group, add_boomerang):
        requirements = []
        approved_hits = NumberHitsApprovedRequirement('GreaterThan', self.min_hits)
        percentage_approved = PercentAssignmentsApprovedRequirement('GreaterThanOrEqualTo', 97)
        locale = MultiLocaleRequirement('In', self.countries)
        boomerang_qual, success = self.create_qualification_type(owner_id=owner_id,
                                                                 name='Boomerang Score #{}'.format(project_group),
                                                                 flag=FLAG_Q_BOOMERANG,
                                                                 description='No description available')
        boomerang = None
        if boomerang_threshold <= int(settings.BOOMERANG_MIDPOINT * 100):
            boomerang_blacklist, success = self.create_qualification_type(owner_id=owner_id,
                                                                          name='Boomerang Waitlist #{}'.format(
                                                                              project_group),
                                                                          flag=FLAG_Q_BOOMERANG,
                                                                          description='No description available',
                                                                          deny=True,
                                                                          boomerang_threshold=boomerang_threshold)
            boomerang = BoomerangRequirement(qualification_type_id=boomerang_blacklist.type_id, comparator=OP_DNE,
                                             integer_value=None)

        else:
            boomerang = BoomerangRequirement(qualification_type_id=boomerang_qual.type_id, comparator=OP_GTEQ,
                                             integer_value=boomerang_threshold)
        requirements.append(locale)
        requirements.append(approved_hits)
        requirements.append(percentage_approved)

        if success and add_boomerang > 0:
            requirements.append(boomerang)
        return Qualifications(requirements), boomerang_qual

    def create_hits(self, project, tasks=None, repetition=None):
        # if project.min_rating > 0:
        #     return 'NOOP'
        if not tasks:
            # noinspection SqlResolve
            query = '''
                SELECT t.id, count(tw.id) worker_count FROM
                crowdsourcing_task t
                LEFT OUTER JOIN crowdsourcing_taskworker tw ON t.id = tw.task_id AND tw.status
                NOT IN (%(skipped)s, %(rejected)s, %(expired)s)
                WHERE project_id = %(project_id)s
                GROUP BY t.id
            '''
            tasks = Task.objects.raw(query, params={'skipped': TaskWorker.STATUS_SKIPPED,
                                                    'rejected': TaskWorker.STATUS_REJECTED,
                                                    'expired': TaskWorker.STATUS_EXPIRED,
                                                    'project_id': project.id})

        max_assignments = project.repetition
        # if str(settings.MTURK_ONLY) == 'True':
        #     max_assignments = project.repetition
        # else:
        #     max_assignments = 1

        qualifications = None
        # if str(settings.MTURK_QUALIFICATIONS) == 'True':
        rated_workers = Rating.objects.filter(origin_id=project.owner_id, origin_type=Rating.RATING_REQUESTER).count()
        add_boomerang = rated_workers > 0
        qualifications, boomerang_qual = self.get_qualifications(owner_id=project.owner_id,
                                                                 boomerang_threshold=int(project.min_rating * 100),
                                                                 project_group=project.group_id,
                                                                 add_boomerang=add_boomerang)
        duration = datetime.timedelta(
            minutes=project.task_time) if project.task_time is not None else datetime.timedelta(days=7)
        lifetime = project.deadline - timezone.now() if project.deadline is not None else datetime.timedelta(
            days=7)
        qualifications_mask = 0
        if qualifications is not None:
            qualifications_mask = FLAG_Q_LOCALE + FLAG_Q_HITS + FLAG_Q_RATE + FLAG_Q_BOOMERANG
        hit_type, success = self.create_hit_type(title=project.name, description=self.description, price=project.price,
                                                 duration=duration, keywords=self.keywords,
                                                 approval_delay=datetime.timedelta(days=2), qual_req=qualifications,
                                                 qualifications_mask=qualifications_mask,
                                                 boomerang_threshold=int(project.min_rating * 100),
                                                 owner_id=project.owner_id, boomerang_qual=boomerang_qual)
        if not success:
            return 'FAILURE'
        for task in tasks:
            question = self.create_external_question(task)
            mturk_hit = MTurkHIT.objects.filter(task=task).first()
            if mturk_hit is None:
                hit = self.connection.create_hit(hit_type=hit_type.string_id,
                                                 max_assignments=max_assignments,
                                                 lifetime=lifetime,
                                                 question=question)[0]
                self.set_notification(hit_type_id=hit.HITTypeId)
                mturk_hit = MTurkHIT(hit_id=hit.HITId, hit_type=hit_type, task=task)
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
        task_id = task_hash.encode(task.id)
        url = self.host + '/mturk/task/?taskId=' + task_id
        question = ExternalQuestion(external_url=url, frame_height=frame_height)
        return question

    def update_max_assignments(self, task):
        task = Task.objects.get(id=task['id'])
        mturk_hit = task.mturk_hit
        if not mturk_hit:
            raise MTurkHIT.DoesNotExist("This task is not associated to any mturk hit")
        assignments_completed = task.task_workers.filter(~Q(task_status__in=[TaskWorker.STATUS_REJECTED,
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

    def expire_hit(self, hit_id):
        try:
            self.connection.expire_hit(hit_id)
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

    def create_qualification_type(self, owner_id, name, flag, description, auto_granted=False,
                                  auto_granted_value=None, deny=False, boomerang_threshold=199):
        qualification = MTurkQualification.objects.filter(owner_id=owner_id, flag=flag, name=name).first()
        if qualification is not None:
            if deny:
                workers = MTurkWorkerQualification.objects.filter(
                    qualification__owner_id=owner_id).annotate(avg_score=Avg('score')).filter(
                    avg_score__gt=boomerang_threshold)
                worker_qualification_ids = []
                for worker in workers:
                    if self.revoke_qualification(qualification_type_id=qualification.type_id,
                                                 worker_id=worker.worker):
                        worker_qualification_ids.append(worker.id)
                MTurkWorkerQualification.objects.filter(id__in=worker_qualification_ids).delete()
            return qualification, True
        try:
            qualification_type = self.connection.create_qualification_type(name=name, description=description,
                                                                           status='Active',
                                                                           auto_granted=auto_granted,
                                                                           auto_granted_value=auto_granted_value)[0]
            qualification = MTurkQualification.objects.create(owner_id=owner_id, flag=flag, name=name,
                                                              description=description,
                                                              auto_granted=auto_granted,
                                                              auto_granted_value=auto_granted_value,
                                                              type_id=qualification_type.QualificationTypeId)
            if not deny:
                workers = MTurkWorkerQualification.objects.values('worker').filter(
                    qualification__owner_id=owner_id).annotate(avg_score=Avg('score'))
            else:
                workers = MTurkWorkerQualification.objects.values('worker').filter(
                    qualification__owner_id=owner_id).annotate(avg_score=Avg('score')).filter(
                    avg_score__lt=boomerang_threshold)
            for worker in workers:
                if self.assign_qualification(qualification_type_id=qualification.type_id,
                                             worker_id=worker['worker'],
                                             value=int(worker['avg_score'])):
                    MTurkWorkerQualification.objects.update_or_create(qualification=qualification,
                                                                      worker=worker['worker'],
                                                                      score=int(worker['avg_score']))
            return qualification, True
        except MTurkRequestError:
            return None, False

    def change_hit_type_of_hit(self, hit_id, hit_type_id):
        try:
            result = self.connection.change_hit_type_of_hit(hit_id=hit_id, hit_type=hit_type_id)
        except MTurkRequestError:
            return None, False
        return result, True

    def update_worker_boomerang(self, project_id, worker_id, weight):
        """
        Update boomerang for project
        Args:
            project_id:
            worker_id:
            weight:

        Returns:
            bool
        """
        hit = MTurkHIT.objects.select_related('hit_type__boomerang_qualification').filter(
            task__project_id=project_id).first()
        if hit is not None:
            qualification = hit.hit_type.boomerang_qualification
            worker_qual = MTurkWorkerQualification.objects.filter(qualification=qualification,
                                                                  worker=worker_id).first()
            self.update_score(worker_qual, score=int(weight * 1000))

            workers = MTurkWorkerQualification.objects.values('worker').filter(
                qualification__owner_id=qualification.owner_id, worker=worker_id).annotate(avg_score=Avg('score'))
            if len(workers):
                other_quals = MTurkWorkerQualification.objects.filter(~Q(qualification=qualification),
                                                                      worker=worker_id,
                                                                      overwritten=False)
                for q in other_quals:
                    self.update_score(q, score=int(workers[0]['avg_score']))
        return 'SUCCESS'

    def update_score(self, worker_qual, score):
        if worker_qual is None:
            return False
        try:
            self.connection.update_qualification_score(worker_qual.qualification.type_id, worker_qual.worker, score)
            worker_qual.overwritten = True
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
