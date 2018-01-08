import datetime
import json
from decimal import Decimal, ROUND_UP

import trueskill
from django.conf import settings
from django.db import connection
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from hashids import Hashids
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

from crowdsourcing import constants
from crowdsourcing.exceptions import daemo_error
from crowdsourcing.models import Task, TaskWorker, TaskWorkerResult, UserPreferences, ReturnFeedback, \
    User, MatchGroup, Batch, Match, WorkerMatchScore, MatchWorker
from crowdsourcing.permissions.task import IsTaskOwner, IsQualified  # HasExceededReservedLimit
from crowdsourcing.permissions.util import IsSandbox
from crowdsourcing.serializers.project import ProjectSerializer
from crowdsourcing.serializers.task import *
from crowdsourcing.tasks import update_worker_cache, refund_task, send_return_notification_email
from crowdsourcing.utils import get_model_or_none, hash_as_set, \
    get_review_redis_message, hash_task
from crowdsourcing.validators.project import validate_account_balance
from mturk.tasks import mturk_hit_update, mturk_approve, mturk_reject


def setup_peer_review(review_project, task_workers, is_inter_task, rerun_key, ids_hash):
    previous_matches = MatchWorker.objects.prefetch_related('match__group').filter(task_worker__in=task_workers)
    matched_workers = [mw.task_worker_id for mw in previous_matches]
    workers_to_match = list(set([tw.id for tw in task_workers]) - set(matched_workers))
    batch = Batch.objects.create()
    match_group = MatchGroup.objects.create(batch=batch, rerun_key=rerun_key, hash=ids_hash)

    if len(workers_to_match) % 2 == 1 and len(matched_workers):
        workers_to_match.append(matched_workers[-1:][0])
    generate_matches(workers_to_match, review_project, is_inter_task, match_group)
    return match_group


def generate_matches(task_worker_ids, review_project, is_inter_task, match_group):
    cursor = connection.cursor()
    # noinspection SqlResolve
    query = '''
        SELECT
            tw.id,
            tw.worker_id,
            coalesce(match_workers.mu, 25.0) mu,
            coalesce(match_workers.sigma, 8.333) sigma,
            u.username,
            tw.task_id
        FROM
            crowdsourcing_taskworker tw
        INNER JOIN auth_user u
            ON u.id = tw.worker_id
        LEFT OUTER JOIN (
            SELECT *
            FROM (
                SELECT
                    max_mw.project_group_id,
                    max_mw.worker_id,
                    mw.sigma,
                    mw.mu,
                    tw.id task_worker_id
                FROM crowdsourcing_matchworker mw
                INNER JOIN crowdsourcing_match m
                    ON m.id = mw.match_id
                INNER JOIN crowdsourcing_taskworker tw ON tw.id = mw.task_worker_id
                INNER JOIN crowdsourcing_task t ON t.id = tw.task_id
                INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                INNER JOIN (
                    SELECT
                        p.group_id           project_group_id,
                        tw.worker_id,
                        max(m.submitted_at) submitted_at
                    FROM crowdsourcing_matchworker mw
                    INNER JOIN crowdsourcing_match m ON m.id = mw.match_id
                    INNER JOIN crowdsourcing_taskworker tw ON tw.id = mw.task_worker_id
                    INNER JOIN crowdsourcing_task t ON t.id = tw.task_id
                    INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                    GROUP BY p.group_id, tw.worker_id
                ) max_mw
                    ON max_mw.project_group_id = p.group_id AND max_mw.worker_id = tw.worker_id AND
                        max_mw.submitted_at = m.submitted_at
            ) mw
        ) match_workers
            ON match_workers.task_worker_id = tw.id
        WHERE tw.id = ANY(%(ids)s);
    '''
    cursor.execute(query, {'ids': task_worker_ids})
    worker_scores = cursor.fetchall()
    match_workers = []
    newly_matched = []

    if not is_inter_task:  # TODO add inter task support later
        to_match = {}
        for worker_score in worker_scores:
            task_id = str(worker_score[5])
            if task_id not in to_match:
                to_match[task_id] = []
            to_match[task_id].append(worker_score)

        for task_id in to_match:
            length = len(to_match[task_id])

            for i, worker_score in enumerate(to_match[task_id]):
                if worker_score in newly_matched:
                    continue
                score_one = worker_score

                rating_one = trueskill.Rating(mu=score_one[2], sigma=score_one[3])
                best_quality = 0
                score_two = None
                for inner_ws in to_match[task_id]:
                    if inner_ws != score_one and \
                        (inner_ws not in newly_matched or (length - 1 == i and i % 2 == 0)) and \
                            score_one[1] != inner_ws[1] and score_one[5] == inner_ws[5]:
                        rating_two = trueskill.Rating(mu=inner_ws[2], sigma=inner_ws[3])
                        match_quality = trueskill.quality_1vs1(rating_one, rating_two)
                        if match_quality > best_quality:
                            best_quality = match_quality
                            score_two = inner_ws

                if score_two is not None:
                    newly_matched.append(score_one)
                    newly_matched.append(score_two)
                    task = Task.objects.create(
                        data={"task_workers": [{'username': score_one[4], 'task_worker': score_one[0]},
                                               {'username': score_two[4], 'task_worker': score_two[0]}]},
                        batch_id=match_group.batch_id, project_id=review_project.id, min_rating=1.99)
                    task.group_id = task.id
                    task.save()
                    match = Match.objects.create(group=match_group, task=task)
                    match_workers.append(
                        MatchWorker(match=match, task_worker_id=score_one[0], old_mu=score_one[2],
                                    old_sigma=score_one[3])
                    )
                    match_workers.append(
                        MatchWorker(match=match, task_worker_id=score_two[0], old_mu=score_two[2],
                                    old_sigma=score_two[3])
                    )
    MatchWorker.objects.bulk_create(match_workers)
    # Task.objects.bulk_create(review_tasks)
    return [s[0] for s in newly_matched]


def make_matchups(workers_to_match, project_group_id, review_project, inter_task_review, match_group_id, batch_id):
    matched_workers = []
    for index in xrange(0, len(workers_to_match)):
        if workers_to_match[index] not in matched_workers:
            if len(workers_to_match) - len(matched_workers) == 1:
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
                    second_score = trueskill.Rating(mu=workers_to_match[j]['score'].mu,
                                                    sigma=workers_to_match[j]['score'].sigma)
                    quality = trueskill.quality_1vs1(first_score, second_score)
                    if quality > best_quality:
                        is_intertask_match = False
                        best_quality = quality
                        second_worker = workers_to_match[j]

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
    match_task = Task.objects.create(project=review_project, data=match_data, batch_id=batch_id, min_rating=1.99)
    match_task.group_id = match_task.id
    match_task.save()


def is_final_review(batch_id):
    tasks = Task.objects.prefetch_related('project').filter(batch_id=batch_id)
    if not tasks:
        return False

    expected = tasks[0].project.repetition * tasks.count()
    task_workers = TaskWorker.objects.filter(task__batch_id=batch_id,
                                             status__in=[TaskWorker.STATUS_SUBMITTED,
                                                         TaskWorker.STATUS_ACCEPTED]).count()

    return expected == task_workers


def update_ts_scores(task_worker, winner_id):
    if task_worker.task.project.is_review:
        match = Match.objects.filter(task=task_worker.task).first()
        if match is not None:
            match_workers = MatchWorker.objects.prefetch_related('task_worker').filter(match=match)
            winner = [w for w in match_workers if w.task_worker_id == int(winner_id)][0]
            loser = [w for w in match_workers if w.task_worker_id != int(winner_id)][0]
            winner_project_ts = MatchWorker.objects.prefetch_related('task_worker').filter(
                task_worker__worker=winner.task_worker.worker, match__status=Match.STATUS_COMPLETED).order_by(
                '-match__submitted_at').first()
            loser_project_ts = MatchWorker.objects.prefetch_related('task_worker').filter(
                task_worker__worker=loser.task_worker.worker, match__status=Match.STATUS_COMPLETED).order_by(
                '-match__submitted_at').first()
            loser_ts = trueskill.Rating(mu=loser_project_ts.mu if loser_project_ts is not None else loser.old_mu,
                                        sigma=loser_project_ts.sigma if loser_project_ts is not None
                                        else loser.old_sigma)
            winner_ts = trueskill.Rating(mu=winner_project_ts.mu if winner_project_ts is not None else winner.old_mu,
                                         sigma=winner_project_ts.sigma if winner_project_ts is not None
                                         else winner.old_sigma)
            new_winner_ts, new_loser_ts = trueskill.rate_1vs1(winner_ts, loser_ts)
            winner.mu = new_winner_ts.mu
            winner.sigma = new_winner_ts.sigma
            winner.save()
            loser.mu = new_loser_ts.mu
            loser.sigma = new_loser_ts.sigma
            loser.save()
            match.status = Match.STATUS_COMPLETED
            match.submitted_at = timezone.now()
            match.save()


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_params = ['project_id', 'rerun_key', 'batch_id']
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        try:
            by = request.query_params.get('filter_by', 'project_id')
            if by not in self.filter_params:
                raise serializers.ValidationError(detail=daemo_error("Invalid filter by field."))
            filter_value = request.query_params.get(by, -1)
            task = Task.objects.filter(**{by: filter_value}).order_by('row_number')
            task_serialized = TaskSerializer(task, many=True,
                                             fields=('id', 'data', 'row_number', 'group_id', 'price', 'hash', 'batch'))
            return Response(
                {
                    "results": task_serialized.data,
                    "count": len(task_serialized.data),
                    "next": None,
                    "previous": None
                })
        except Exception:
            return Response([])

    @detail_route(methods=['get'], url_path='assignment-results', permission_classes=[IsTaskOwner])
    def assignment_results(self, request, pk, *args, **kwargs):
        results = TaskWorkerResult.objects.filter(task_worker__task_id=pk)
        response_data = TaskWorkerResultSerializer(instance=results,
                                                   many=True,
                                                   fields=('id', 'template_item', 'result',
                                                           'created_at', 'updated_at', 'attachment',
                                                           'assignment_id')).data
        return Response(response_data)

    @list_route(methods=['get'], url_path='list-data')
    def list_conflicts(self, request, *args, **kwargs):
        project = request.query_params.get('project', -1)
        offset = int(request.query_params.get('offset', 0))

        # noinspection SqlResolve
        query = '''
            SELECT t.id, t.data, t.row_number
            FROM crowdsourcing_task t
              INNER JOIN (

                           SELECT t.group_id, count(tw.id)
                           FROM crowdsourcing_task t
                             LEFT OUTER JOIN crowdsourcing_taskworker tw ON (t.id = tw.task_id
                             AND tw.status NOT IN (4, 6, 7))
                           WHERE exclude_at IS NULL AND t.deleted_at IS NULL AND t.project_id <> (%(project_id)s)
                           GROUP BY t.group_id HAVING count(tw.id)>0) all_tasks ON all_tasks.group_id = t.group_id
            WHERE project_id = (%(project_id)s) AND deleted_at IS NULL
            LIMIT 10 OFFSET (%(seek)s)
        '''

        tasks = list(Task.objects.raw(query, params={'project_id': project, 'seek': offset}))
        headers = []
        if len(tasks) > 0:
            headers = tasks[0].data.keys()[:4]
        serializer = TaskSerializer(tasks, many=True, fields=('id', 'data', 'row_number'))
        return Response({'headers': headers, 'tasks': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = TaskSerializer(instance=obj,
                                    fields=('id', 'data', 'row_number', 'price', 'hash',
                                            # todo 'template', 'project_data', @DM removed these
                                            'worker_count', 'completed', 'total'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        task.delete()
        return Response({'status': 'deleted task'})

    def create(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id')
        project = models.Project.objects.filter(id=project_id, owner=request.user).first()
        if project is None:
            return Response({"message": "Project not found!"}, status=status.HTTP_404_NOT_FOUND)
        price = project.price
        if project.allow_price_per_task and project.task_price_field in request.data and \
                request.data[project.task_price_field] is not None:
            price = request.data[project.task_price_field]
        to_pay = price * project.repetition
        if project.status == models.Project.STATUS_ARCHIVED:
            return Response({"message": "This project has been archived."}, status=status.HTTP_400_BAD_REQUEST)
        elif project.status != models.Project.STATUS_DRAFT:
            validate_account_balance(request, Decimal(to_pay).quantize(Decimal('.01'), rounding=ROUND_UP))
        task_hash = hash_task(data=request.data.get('data', {}))
        created = False
        with transaction.atomic():
            task = models.Task.objects.filter(hash=task_hash, project=project).first()
            if task is None:
                created = True
                task = models.Task.objects.create(data=request.data.get('data', {}),
                                                  row_number=request.data.get('row_number'), hash=task_hash,
                                                  project=project)
                task.group_id = task.id
                task.save()
                project.amount_due += to_pay
                project.save()

        return Response({"id": task.id, "hash": task_hash, "group_id": task.group_id, "created": created})

    @detail_route(methods=['get'], url_path='results')
    def results(self, request, *args, **kwargs):
        task = self.get_object()
        if task.project.owner != request.user:
            return Response({"message": "Task not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "next": None,
            "previous": None,
            "count": 0,
            "results": []

        })

    @detail_route(methods=['get'])
    def retrieve_with_data(self, request, *args, **kwargs):
        task = self.get_object()
        task_worker = TaskWorker.objects.filter(worker=request.user, task=task).first()
        serializer = TaskSerializer(instance=task,
                                    fields=('id', 'template', 'project_data', 'status', 'price'),
                                    context={'task_worker': task_worker})
        requester_alias = task.project.owner.profile.handle
        project = task.project.id
        is_review = task.project.is_review
        timeout = task.project.timeout
        worker_timestamp = task_worker.created_at
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        last_rating = models.Rating.objects.filter(origin=request.user, origin_type=models.Rating.RATING_WORKER,
                                                   target=task.project.owner,
                                                   task__project__group_id=task.project.group_id).order_by(
            '-id').first()
        if last_rating is None:
            rating = {
                "target": task.project.owner_id,
                "weight": 2.0,
                "origin_type": models.Rating.RATING_WORKER
            }
        else:
            rating = {
                "target": task.project.owner_id,
                "weight": last_rating.weight,
                "origin_type": models.Rating.RATING_WORKER
            }

        if timeout is not None:
            time_left = int(timeout.total_seconds() - (now - worker_timestamp).total_seconds())
        else:
            time_left = None

        auto_accept = False
        feedback = task_worker.return_feedback.first()
        user_prefs = get_model_or_none(UserPreferences, user=request.user)
        is_rejected = task_worker.collective_rejection is not None if task_worker is not None else False
        if user_prefs is not None:
            auto_accept = user_prefs.auto_accept

        return Response({'data': serializer.data,
                         'requester_alias': requester_alias,
                         'owner_id': task.project.owner_id,
                         'requester_rating': rating,
                         'project': project,
                         'return_feedback': feedback.body if feedback is not None else None,
                         'is_review': is_review,
                         'time_left': time_left,
                         'has_expired': time_left <= 0,
                         'auto_accept': auto_accept,
                         'task_worker_id': task_worker.id,
                         'is_qualified': task_worker.is_qualified,
                         'is_rejected': is_rejected
                         }, status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def retrieve_peer_review(self, request, *args, **kwargs):
        task = self.get_object()
        project = task.project_id
        task_workers = []
        if task.data['task_workers']:
            for worker in task.data['task_workers']:
                task_workers.append(worker['task_worker'])

        return Response({'project': project,
                         'task_workers': sorted(task_workers)}, status.HTTP_200_OK)

    @list_route(methods=['get'])
    def list_by_project(self, request, **kwargs):
        tasks = Task.objects.filter(project=request.query_params.get('project_id')).order_by('id')

        task_serializer = TaskSerializer(instance=tasks, many=True, fields=('id', 'updated_at',
                                                                            'worker_count', 'completed', 'total'))
        return Response(data=task_serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def list_comments(self, request, **kwargs):
        comments = models.TaskComment.objects.filter(task=kwargs['pk'])
        serializer = TaskCommentSerializer(instance=comments, many=True, fields=('comment', 'id',))
        response_data = {
            'task': kwargs['pk'],
            'comments': serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def post_comment(self, request, **kwargs):
        serializer = TaskCommentSerializer(data=request.data)
        task_comment_data = {}
        if serializer.is_valid():
            comment = serializer.create(task=kwargs['pk'], sender=request.user)
            task_comment_data = TaskCommentSerializer(comment, fields=('id', 'comment',)).data

        return Response(task_comment_data, status.HTTP_200_OK)

    @list_route(methods=['post'], url_path='relaunch-all')
    def relaunch_all(self, request, *args, **kwargs):
        project_id = request.query_params.get('project', -1)
        project = get_object_or_404(models.Project, pk=project_id)
        tasks = models.Task.objects.active().filter(~Q(project_id=project_id), project__group_id=project.group_id)
        self.serializer_class().bulk_update(tasks, {'exclude_at': project_id})
        return Response(data={}, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='relaunch')
    def relaunch(self, request, *args, **kwargs):
        task = self.get_object()
        tasks = models.Task.objects.active().filter(~Q(id=task.id), group_id=task.group_id)
        self.serializer_class().bulk_update(tasks, {'exclude_at': task.project_id})
        return Response(data={}, status=status.HTTP_200_OK)

    @list_route(methods=['post'], url_path='peer-review')
    def peer_review(self, request, *args, **kwargs):
        task_worker_ids = request.data.get('task_workers', [])
        is_inter_task = request.data.get('inter_task_review', False)
        rerun_key = request.data.get('rerun_key', None)
        ids_hash = hash_as_set(task_worker_ids)

        if len(task_worker_ids) < 2:
            raise serializers.ValidationError(detail=daemo_error("We need at least two workers to run peer review"))
        match_group = MatchGroup.objects.filter(hash=ids_hash, rerun_key=rerun_key).first()

        if match_group is not None:
            if is_final_review(match_group.batch_id):
                from crowdsourcing.viewsets.rating import WorkerRequesterRatingViewset
                scores = WorkerRequesterRatingViewset.get_true_skill_ratings(match_group.id)
                return Response(data={"match_group_id": match_group.id, "scores": scores}, status=status.HTTP_200_OK)
            return Response(data={"match_group_id": match_group.id}, status=status.HTTP_200_OK)

        task_workers = TaskWorker.objects.prefetch_related('task__project').filter(id__in=task_worker_ids, status__in=[
            TaskWorker.STATUS_ACCEPTED])
        if len(task_workers) != len(task_worker_ids):
            raise serializers.ValidationError(
                detail=daemo_error("Invalid task worker ids or not all of the responses have been approved."))

        review_project = models.Project.objects.filter(parent_id=task_workers[0].task.project.group_id, is_review=True,
                                                       deleted_at__isnull=True).first()

        if review_project is not None and review_project.price is not None:
            with transaction.atomic():
                match_group = setup_peer_review(review_project, task_workers, is_inter_task,
                                                rerun_key, ids_hash)
            return Response(status=status.HTTP_201_CREATED, data={'match_group_id': match_group.id})
        else:
            raise serializers.ValidationError(detail=daemo_error("This project has no review set up."))

    @detail_route(methods=['get'], url_path='is-done')
    def is_done(self, request, *args, **kwargs):
        group_id = self.get_object().group_id
        # noinspection SqlResolve
        query = '''
            SELECT greatest(t_count.completed, p.repetition) expected, t_count.completed, p.repetition
            FROM crowdsourcing_task t
              INNER JOIN (SELECT
                            group_id,
                            max(id) id
                          FROM crowdsourcing_task
                          WHERE deleted_at IS NULL
                          GROUP BY group_id) t_max ON t_max.id = t.id
              INNER JOIN crowdsourcing_project p ON p.id = t.project_id
              INNER JOIN (
                           SELECT
                             t.group_id,
                             coalesce(sum(t.others), 0) completed
                           FROM (
                                  SELECT
                                    t.group_id,
                                    CASE WHEN tw.id IS NOT NULL
                                      THEN 1
                                    ELSE 0 END OTHERS
                                  FROM crowdsourcing_task t
                                    LEFT OUTER JOIN crowdsourcing_taskworker tw
                                      ON (t.id = tw.task_id AND tw.status IN (2, 3))
                                  WHERE t.exclude_at IS NULL AND t.deleted_at IS NULL) t
                           GROUP BY t.group_id) t_count ON t_count.group_id = t.group_id
            WHERE t.group_id = (%(group_id)s);
        '''
        cursor = connection.cursor()
        cursor.execute(query, {'group_id': group_id})
        task = cursor.fetchall()[0] if cursor.rowcount > 0 else None
        done = task[0] <= task[1]
        return Response(data={"is_done": done, 'expected': task[0]},
                        status=status.HTTP_200_OK)


class TaskWorkerViewSet(viewsets.ModelViewSet):
    queryset = TaskWorker.objects.all()
    serializer_class = TaskWorkerSerializer
    permission_classes = [IsAuthenticated, IsQualified]

    # permission_classes = [IsAuthenticated, HasExceededReservedLimit]

    # lookup_field = 'task__id'

    def create(self, request, *args, **kwargs):
        project = models.Project.objects.get(id=request.data.get('project', None))
        latest_revision = models.Project.objects.filter(group_id=project.group_id).order_by('-id').first()
        serializer = TaskWorkerSerializer()
        with transaction.atomic():
            instance, http_status = serializer.create(worker=request.user,
                                                      project=latest_revision.id, group_id=latest_revision.group_id)
        serialized_data = {}
        if http_status == 200:
            serialized_data = TaskWorkerSerializer(instance=instance, fields=('id', 'task', 'project_data')).data
            update_worker_cache.delay([instance.worker_id], constants.TASK_ACCEPTED)
            mturk_hit_update.delay({'id': instance.task.id})
        return Response(serialized_data, http_status)

    @list_route(url_path='has-project-permission')
    def has_project_permission(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        serializer = TaskWorkerSerializer()
        obj = self.queryset.get(id=kwargs['pk'], worker=request.user)
        auto_accept = False
        user_prefs = get_model_or_none(UserPreferences, user=request.user)
        instance, http_status = None, status.HTTP_204_NO_CONTENT
        obj.status = TaskWorker.STATUS_SKIPPED
        obj.save()
        obj.sessions.all().filter(ended_at__isnull=True).update(ended_at=timezone.now())
        if user_prefs is not None:
            auto_accept = user_prefs.auto_accept
        if auto_accept:
            instance, http_status = serializer.create(worker=request.user, project=obj.task.project_id,
                                                      id=kwargs['pk'], task_id=obj.task_id)
            while http_status == 200 and not instance.is_qualified:
                instance, http_status = serializer.create(worker=request.user, project=obj.task.project_id,
                                                          id=kwargs['pk'], task_id=obj.task_id)

        # refund_task.delay([{'id': obj.id}])
        update_worker_cache.delay([obj.worker_id], constants.TASK_SKIPPED)
        # mturk_hit_update.delay({'id': obj.task.id})
        serialized_data = {}
        if http_status == status.HTTP_200_OK:
            serialized_data = TaskWorkerSerializer(instance=instance).data
        return Response(serialized_data, http_status)

    @list_route(methods=['post'], url_path='bulk-update-status')
    def bulk_update_status(self, request, *args, **kwargs):
        task_status = request.data.get('status', -1)
        all_task_workers = TaskWorker.objects.filter(id__in=tuple(request.data.get('workers', [])))
        relevant_task_workers = all_task_workers.exclude(status=task_status)

        workers = relevant_task_workers.values_list('worker_id', flat=True)
        task_worker_ids = relevant_task_workers.values_list('id', flat=True)

        if task_status == TaskWorker.STATUS_RETURNED:
            update_worker_cache.delay(list(workers), constants.TASK_RETURNED)
        elif task_status == TaskWorker.STATUS_REJECTED:
            update_worker_cache.delay(list(workers), constants.TASK_REJECTED)
            mturk_reject(list(task_worker_ids))
        elif task_status == TaskWorker.STATUS_ACCEPTED:
            mturk_approve.delay(list(task_worker_ids))

        all_task_workers.update(status=task_status, updated_at=timezone.now())
        if task_status == TaskWorker.STATUS_ACCEPTED:
            all_task_workers.update(approved_at=timezone.now())

        return Response(TaskWorkerSerializer(instance=all_task_workers, many=True,
                                             fields=('id', 'task', 'status',
                                                     'worker_alias', 'updated_delta')).data, status.HTTP_200_OK)

    @list_route(methods=['post'], url_path='accept-all')
    def accept_all(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id', -1)
        project = models.Project.objects.filter(id=project_id).first()
        up_to = request.query_params.get('up_to')
        if up_to is None:
            up_to = timezone.now()
        from itertools import chain

        task_workers = TaskWorker.objects.filter(status=TaskWorker.STATUS_SUBMITTED,
                                                 submitted_at__lte=up_to,
                                                 task__project_id=project_id)
        list_workers = list(chain.from_iterable(task_workers.values_list('id')))

        update_worker_cache.delay(list(task_workers.values_list('worker_id', flat=True)), constants.TASK_APPROVED)
        with transaction.atomic():
            task_workers.update(status=TaskWorker.STATUS_ACCEPTED, updated_at=timezone.now(),
                                approved_at=timezone.now())

            latest_revision = models.Project.objects.filter(~Q(status=models.Project.STATUS_DRAFT),
                                                            group_id=project.group_id) \
                .order_by('-id').first()
            latest_revision.amount_due -= Decimal(latest_revision.price * len(list_workers))
            latest_revision.save()
        return Response(data=list_workers, status=status.HTTP_200_OK)

    @list_route(methods=['post'], url_path='approve-worker')
    def approve_worker(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id', -1)
        project = models.Project.objects.filter(id=project_id).first()
        up_to = request.query_params.get('up_to')
        worker_id = request.query_params.get('worker_id')
        if up_to is None:
            up_to = timezone.now()
        from itertools import chain

        task_workers = TaskWorker.objects.filter(status=TaskWorker.STATUS_SUBMITTED,
                                                 submitted_at__lte=up_to,
                                                 worker_id=worker_id,
                                                 task__project_id=project_id)
        list_workers = list(chain.from_iterable(task_workers.values_list('id')))

        update_worker_cache.delay(list(task_workers.values_list('worker_id', flat=True)), constants.TASK_APPROVED)
        with transaction.atomic():
            task_workers.update(status=TaskWorker.STATUS_ACCEPTED, updated_at=timezone.now(),
                                approved_at=timezone.now())

            latest_revision = models.Project.objects.filter(~Q(status=models.Project.STATUS_DRAFT),
                                                            group_id=project.group_id) \
                .order_by('-id').first()
            latest_revision.amount_due -= Decimal(latest_revision.price * len(list_workers))
            latest_revision.save()
        return Response(data=list_workers, status=status.HTTP_200_OK)

    @list_route(methods=['get'], url_path='list-my-tasks')
    def list_my_tasks(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id', -1)
        task_workers = TaskWorker.objects.exclude(status=TaskWorker.STATUS_SKIPPED). \
            filter(worker=request.user, task__project_id=project_id)
        serializer = TaskWorkerSerializer(instance=task_workers, many=True,
                                          fields=(
                                              'id', 'status', 'task',
                                              'is_paid', 'return_feedback'))
        response_data = {
            "project_id": project_id,
            "tasks": serializer.data
        }
        return Response(data=response_data, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def drop_saved_tasks(self, request, *args, **kwargs):
        task_ids = request.data.get('task_ids', [])
        for task_id in task_ids:
            mturk_hit_update.delay({'id': task_id})
        task_workers = self.queryset.filter(task_id__in=task_ids, worker=request.user)
        task_workers.update(
            status=TaskWorker.STATUS_SKIPPED, updated_at=timezone.now())
        tw_serialized = self.serializer_class(task_workers, fields=('id',), many=True).data
        refund_task.delay(tw_serialized)
        return Response(data={'task_ids': task_ids}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def bulk_pay_by_project(self, request, *args, **kwargs):
        project = request.data.get('project')
        task_workers = TaskWorker.objects.filter(task__project=project).filter(
            Q(status=TaskWorker.STATUS_ACCEPTED) | Q(status=TaskWorker.STATUS_REJECTED))
        task_workers.update(is_paid=True, updated_at=timezone.now())
        return Response('Success', status.HTTP_200_OK)

    @list_route(methods=['get'], url_path="get-taskworker")
    def get_task_worker(self, request, *args, **kwargs):
        task_worker_id = request.query_params.get('taskworker_id', -1)
        task_worker = TaskWorker.objects.get(id=task_worker_id)
        serializer = TaskWorkerSerializer(instance=task_worker,
                                          fields=(
                                              'id', 'results', 'worker_alias', 'worker_rating', 'worker', 'status',
                                              'task'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['get'], url_path="list-submissions")
    def list_submissions(self, request, *args, **kwargs):
        task_id = request.query_params.get('task_id', -1)
        workers = TaskWorker.objects.filter(status__in=[2, 3, 5], task_id=task_id)
        serializer = TaskWorkerSerializer(instance=workers, many=True,
                                          fields=('id', 'results',
                                                  'worker_alias', 'worker_rating', 'worker', 'status'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='retrieve-with-data')
    def retrieve_with_data(self, request, *args, **kwargs):
        task_worker = self.get_object()
        task = task_worker.task
        serializer = TaskSerializer(instance=task,
                                    fields=('id', 'template',),
                                    context={'task_worker': task_worker})
        is_review = task.project.is_review
        response_data = {
            'task': serializer.data,
            'worker_alias': task_worker.worker.username,
            'is_review': is_review,
            'is_rejected': task_worker.collective_rejection is not None if task_worker is not None else False,
            'id': task_worker.id,
        }
        return Response(response_data, status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='preview')
    def preview(self, request, *args, **kwargs):
        task_worker = self.get_object()
        serializer = TaskWorkerSerializer(instance=task_worker,
                                          fields=('id', 'worker', 'status', 'task',
                                                  'worker_alias', 'project_data',
                                                  'submitted_at', 'approved_at', 'task_template'))
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='other-submissions')
    def list_other_submissions(self, request, pk, *args, **kwargs):
        task_worker = self.get_object()
        other_task_workers = self.queryset.filter(~Q(id=pk), status__in=[2, 3, 5], task=task_worker.task)
        serializer = TaskWorkerSerializer(instance=other_task_workers, many=True,
                                          fields=('id', 'results',
                                                  'worker_alias', 'worker', 'status', 'task',
                                                  'task_template'))
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def collective_reject(self, request, *args, **kwargs):
        task_worker = self.get_object()
        serializer = CollectiveRejectionSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                collective_rejection = serializer.create()
                task_worker.collective_rejection = collective_rejection
                task_worker.save()
            return Response(data={"message": "Response successfully submitted."}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], url_path='approve')
    def approve(self, request, *args, **kwargs):
        return Response({})

    @detail_route(methods=['post'], url_path='return')
    def return_for_revision(self, request, *args, **kwargs):
        return Response({})

    @detail_route(methods=['post'], url_path='reject')
    def reject(self, request, *args, **kwargs):
        return Response({})

    @detail_route(methods=['post'], url_path='override-return')
    def override_return(self, request, *args, **kwargs):
        instance = self.queryset.filter(pk=kwargs.get('pk'), worker=request.user).first()
        if instance is None:
            return Response({"message": "Assignment not found!"}, status=status.HTTP_404_NOT_FOUND)
        instance.submitted_at = timezone.now()
        instance.status = TaskWorker.STATUS_SUBMITTED
        instance.save()
        return Response({"message": "Assignment updated successfully!"})


class TaskWorkerResultViewSet(viewsets.ModelViewSet):
    queryset = TaskWorkerResult.objects.all()
    serializer_class = TaskWorkerResultSerializer

    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        task_worker_result = self.queryset.filter(id=kwargs['pk'])[0]
        status = TaskWorkerResult.STATUS_CREATED

        if 'status' in request.data:
            status = request.data['status']

        task_worker_result.status = status
        task_worker_result.save()
        return Response("Success")

    def retrieve(self, request, *args, **kwargs):
        result = self.get_object()
        serializer = TaskWorkerResultSerializer(instance=result)
        return Response(serializer.data)

    @list_route(methods=['post'], url_path="upload-file")
    def upload_file(self, request, *args, **kwargs):
        uploaded_file = request.data.get('file')
        file_obj = models.FileResponse.objects.create(file=uploaded_file, owner=request.user, name=uploaded_file.name)
        return Response({"id": file_obj.id})

    @list_route(methods=['post'], url_path="attach-file")
    def attach_file(self, request, *args, **kwargs):
        task_worker_id = request.data.get('task_worker_id')
        template_item_id = request.data.get('template_item_id')
        file_id = request.data.get('file_id')
        task_worker = models.TaskWorker.objects.filter(id=task_worker_id, worker=request.user).first()
        if task_worker is None:
            return Response(daemo_error("Task worker not found!"), status=status.HTTP_404_NOT_FOUND)
        template_item = models.TemplateItem.objects.filter(id=template_item_id, type='file_upload').first()
        if template_item is None:
            return Response(daemo_error("Template item not found!"), status=status.HTTP_404_NOT_FOUND)
        task_worker_result = models.TaskWorkerResult.objects.filter(task_worker=task_worker,
                                                                    template_item=template_item).first()
        file_response = models.FileResponse.objects.filter(id=file_id, owner=request.user).first()

        if file_response is None:
            return Response(daemo_error("Attachment not found!"), status=status.HTTP_404_NOT_FOUND)
        if task_worker_result is None:
            task_worker_result = models.TaskWorkerResult.objects.create(task_worker=task_worker,
                                                                        template_item=template_item,
                                                                        attachment=file_response)
        else:
            task_worker_result.attachment = file_response
            task_worker_result.save()

        return Response({"message": "OK", "id": task_worker_result.id, "name": file_response.name})

    @list_route(methods=['post'], url_path="submit-results")
    def submit_results(self, request, mock=False, *args, **kwargs):
        task = request.data.get('task', None)
        auto_accept = request.data.get('auto_accept', False)
        template_items = request.data.get('items', [])
        task_status = request.data.get('status', None)
        saved = request.data.get('saved')
        task_worker = None
        if mock:
            task_status = TaskWorker.STATUS_SUBMITTED
            template_items = kwargs['items']
            task_worker = kwargs['task_worker']
        if not mock:
            task_worker = TaskWorker.objects.prefetch_related('task', 'task__project').get(worker=request.user,
                                                                                           task=task)
        if task_worker.status == TaskWorker.STATUS_SKIPPED and not task_worker.is_qualified:
            return Response(daemo_error("You are not allowed to submit this task!"),
                            status=status.HTTP_400_BAD_REQUEST)
        elif task_worker.status == TaskWorker.STATUS_EXPIRED:
            return Response(daemo_error("This task has expired!"), status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():

            task_worker_results = TaskWorkerResult.objects.filter(~Q(template_item__type='file_upload'),
                                                                  task_worker_id=task_worker.id,
                                                                  template_item_id__in=[t['template_item'] for t in
                                                                                        template_items])

            if task_status == TaskWorker.STATUS_IN_PROGRESS:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True, partial=True)
            else:
                serializer = TaskWorkerResultSerializer(data=template_items, many=True)

            if serializer.is_valid():
                task_worker.status = task_status
                task_worker.attempt += 1
                task_worker.submitted_at = timezone.now()
                task_worker.save()
                task_worker.sessions.all().filter(ended_at__isnull=True).update(ended_at=timezone.now())
                # check_project_completed.delay(project_id=task_worker.task.project_id)
                # #send_project_completed_email.delay(project_id=task_worker.task.project_id)
                if task_status == TaskWorker.STATUS_SUBMITTED:
                    redis_publisher = RedisPublisher(facility='bot', users=[task_worker.task.project.owner])
                    front_end_publisher = RedisPublisher(facility='notifications',
                                                         users=[task_worker.task.project.owner])

                    task = task_worker.task
                    message = {
                        "type": "REGULAR",
                        "payload": {
                            'project_id': task_worker.task.project_id,
                            'project_key': ProjectSerializer().get_hash_id(task_worker.task.project),
                            'task_id': task_worker.task_id,
                            'task_group_id': task_worker.task.group_id,
                            'taskworker_id': task_worker.id,
                            'worker_id': task_worker.worker_id
                        }
                    }
                    if task.project.is_review:
                        match_group = MatchGroup.objects.get(batch=task.batch)
                        if is_final_review(match_group.batch_id):
                            message = get_review_redis_message(match_group.id, ProjectSerializer().get_hash_id(
                                task_worker.task.project))
                    message = RedisMessage(json.dumps(message))

                    redis_publisher.publish_message(message)
                    front_end_publisher.publish_message(RedisMessage(
                        json.dumps({"event": "TASK_SUBMITTED",
                                    'project_key': ProjectSerializer().get_hash_id(task_worker.task.project),
                                    "project_gid": task_worker.task.project.group_id})))
                existing_results = [t.template_item_id for t in task_worker_results]
                if len(existing_results) != 0:
                    serializer.update(task_worker_results, serializer.validated_data)
                new_items = []
                for item in template_items:
                    if item['template_item'] not in existing_results:
                        new_items.append(item)
                if len(new_items):
                    serializer.create(task_worker=task_worker, validated_data=new_items)

                update_worker_cache.delay([task_worker.worker_id], constants.TASK_SUBMITTED)
                if task_worker_results.count():
                    winner_id = task_worker_results[0].result
                    update_ts_scores(task_worker, winner_id)
                if task_status == TaskWorker.STATUS_IN_PROGRESS or saved or mock:
                    return Response('Success', status.HTTP_200_OK)
                elif task_status == TaskWorker.STATUS_SUBMITTED and not saved:

                    if not auto_accept:
                        serialized_data = {}
                        http_status = 204
                        return Response(serialized_data, http_status)

                    task_worker_serializer = TaskWorkerSerializer()
                    instance, http_status = task_worker_serializer.create(
                        worker=request.user, project=task_worker.task.project_id)
                    while hasattr(instance, 'is_qualified') and not instance.is_qualified and http_status == 200:
                        instance, http_status = task_worker_serializer.create(
                            worker=request.user, project=task_worker.task.project_id)
                    serialized_data = {}

                    if http_status == status.HTTP_200_OK:
                        serialized_data = TaskWorkerSerializer(instance=instance).data
                        update_worker_cache.delay([task_worker.worker_id], constants.TASK_ACCEPTED)

                    return Response(serialized_data, http_status)
            else:
                raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['post'], url_path="mock-results", permission_classes=[IsSandbox, IsTaskOwner])
    def mock_results(self, request, *args, **kwargs):
        task_id = request.data.get('task_id', None)
        results = request.data.get('results', [])
        existing_workers = TaskWorker.objects.values('worker') \
            .filter(task_id=task_id,
                    status__in=[TaskWorker.STATUS_ACCEPTED,
                                TaskWorker.STATUS_IN_PROGRESS,
                                TaskWorker.STATUS_SUBMITTED,
                                TaskWorker.STATUS_RETURNED]).values_list(
            'worker', flat=True)
        new_workers = User.objects.filter(~Q(id__in=existing_workers),
                                          username__startswith='mockworker.')[:len(results)]
        for i, worker in enumerate(new_workers):
            task_worker, created = TaskWorker.objects.get_or_create(worker=worker, task_id=task_id)
            self.submit_results(request, mock=True, items=results[i]['items'], task_worker=task_worker)
        return Response(data={"message": "{} results submitted".format(len(new_workers))},
                        status=status.HTTP_201_CREATED)


class ExternalSubmit(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ExternalSubmit, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        identifier = request.query_params.get('daemo_id', False)
        if not identifier:
            raise serializers.ValidationError(detail=daemo_error("Missing identifier"))
        try:

            identifier_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
            if len(identifier_hash.decode(identifier)) == 0:
                raise serializers.ValidationError(detail=daemo_error("Invalid identifier"))
            task_worker_id, task_id, template_item_id = identifier_hash.decode(identifier)
            # template_item = models.TemplateItem.objects.get(id=template_item_id)
            # task = models.Task.objects.get(id=task_id)
            # source_url = None
            # if template_item.aux_attributes['src']:
            #     source_url = urlsplit(template_item.aux_attributes['src'])
            # else:
            #     source_url = urlsplit(task.data[template_item.aux_attributes['data_source']])
            # if 'HTTP_REFERER' not in request.META.keys():
            #     return Response(data={"message": "Missing referer"}, status=status.HTTP_403_FORBIDDEN)
            # referer_url = urlsplit(request.META['HTTP_REFERER'])
            # if referer_url.netloc != source_url.netloc or referer_url.scheme != source_url.scheme:
            #     return Response(data={"message": "Referer does not match source"}, status=status.HTTP_403_FORBIDDEN)

            redis_publisher = RedisPublisher(facility='external', broadcast=True)
            task_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
            message = RedisMessage(json.dumps({"task_id": task_hash.encode(task_id),
                                               "daemo_id": identifier,
                                               "template_item": template_item_id
                                               }))
            redis_publisher.publish_message(message)
            with transaction.atomic():
                task_worker = TaskWorker.objects.get(id=task_worker_id, task_id=task_id)
                task_worker_result, created = TaskWorkerResult.objects.get_or_create(task_worker_id=task_worker.id,
                                                                                     template_item_id=template_item_id)
                # only accept in progress, submitted, or returned tasks
                if task_worker.status in [1, 2, 5]:
                    task_worker.status = TaskWorker.STATUS_SUBMITTED
                    task_worker.submitted_at = timezone.now()
                    task_worker.save()
                    task_worker_result.result = request.data
                    task_worker_result.save()
                    update_worker_cache.delay([task_worker.worker_id], constants.TASK_SUBMITTED)
                    # check_project_completed.delay(project_id=task_worker.task.project_id)
                    return Response(request.data, status=status.HTTP_200_OK)
                else:
                    raise serializers.ValidationError(detail=daemo_error("Task cannot be modified now"))
        except ValueError:
            raise serializers.ValidationError(detail=daemo_error("Missing identifier"))
        except Exception:
            raise serializers.ValidationError(detail=daemo_error("Something went wrong!"))

    def get(self, request, *args, **kwargs):
        identifier = request.query_params.get('daemo_id', False)
        identifier_hash = Hashids(salt=settings.SECRET_KEY, min_length=settings.ID_HASH_MIN_LENGTH)
        if len(identifier_hash.decode(identifier)) == 0:
            raise serializers.ValidationError(detail=daemo_error("Invalid identifier"))
        task_worker_id, task_id, template_item_id = identifier_hash.decode(identifier)
        result = TaskWorkerResult.objects.filter(task_worker_id=task_worker_id,
                                                 template_item_id=template_item_id).first()
        if result is not None:
            return Response(result.result)
        else:
            return Response({})


class ReturnFeedbackViewSet(viewsets.ModelViewSet):
    queryset = ReturnFeedback.objects.all()
    serializer_class = ReturnFeedbackSerializer

    def create(self, request, *args, **kwargs):
        tw_status = request.data.get('status', TaskWorker.STATUS_RETURNED)
        serializer = ReturnFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.create()
            send_return_notification_email.delay(instance.id, tw_status == TaskWorker.STATUS_REJECTED)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError(detail=serializer.errors)
