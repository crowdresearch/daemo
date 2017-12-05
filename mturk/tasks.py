from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Q
from pandas import *

from crowdsourcing.crypto import AESUtil
from crowdsourcing.models import Project, TaskWorker, Task, Rating
from csp.celery import app as celery_app
from csp.settings import SITE_HOST, AWS_DAEMO_KEY
from mturk.interface import MTurkProvider
from mturk.models import MTurkHIT


@celery_app.task(ignore_result=True)
def mturk_publish():
    projects = Project.objects.active().filter(~Q(owner__mturk_account=None),
                                               # min_rating__lt=MTURK_THRESHOLD,
                                               post_mturk=True, status=Project.STATUS_IN_PROGRESS)
    for project in projects:
        try:
            provider = get_provider(project.owner)
            provider.create_hits(project)
        except Exception:
            pass
    return {'message': 'SUCCESS'}


@celery_app.task(ignore_result=True)
def mturk_hit_update(task):
    user_id = Task.objects.values('project__owner').get(id=task['id'])['project__owner']
    user = User.objects.get(id=user_id)
    provider = get_provider(user)
    if provider is None:
        return
    return provider.update_max_assignments(task)


@celery_app.task(ignore_result=True)
def mturk_approve(list_workers):
    if len(list_workers) == 0:
        return

    user_id = TaskWorker.objects.values('task__project__owner').get(
        id=list_workers[0])['task__project__owner']
    user = User.objects.get(id=user_id)
    provider = get_provider(user)
    if provider is None:
        return
    for task_worker_id in list_workers:
        provider.approve_assignment({'id': task_worker_id})
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def mturk_reject(list_workers):
    if len(list_workers) == 0:
        return

    user_id = TaskWorker.objects.values('task__project__owner').get(
        id=list_workers[0])['task__project__owner']
    user = User.objects.get(id=user_id)

    provider = get_provider(user)
    if provider is None:
        return

    for task_worker_id in list_workers:
        provider.reject_assignment({'id': task_worker_id})

        # add new assignment every time a assignment is rejected
        hit_id = TaskWorker.objects.values('task__mturk_hit__hit_id').get(id=task_worker_id)['task__mturk_hit__hit_id']
        provider.add_assignments(hit_id=hit_id, increment=1)
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def mturk_update_status(project):
    user_id = Project.objects.values('owner').get(id=project['id'])['owner']
    user = User.objects.get(id=user_id)
    provider = get_provider(user)
    if provider is None:
        return
    hits = MTurkHIT.objects.filter(task__project_id=project['id'])
    for hit in hits:
        if project['status'] == Project.STATUS_IN_PROGRESS:
            provider.extend_hit(hit.hit_id)
            hit.status = MTurkHIT.STATUS_IN_PROGRESS
        elif project['status'] == Project.STATUS_CROWD_REJECTED:
            # TODO delete? for now only expire
            provider.expire_hit(hit.hit_id)
            hit.status = MTurkHIT.STATUS_EXPIRED
        else:
            provider.expire_hit(hit.hit_id)
            hit.status = MTurkHIT.STATUS_EXPIRED
        hit.save()
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def mturk_hit_collective_reject(task_worker):
    task_worker_obj = TaskWorker.objects.prefetch_related('task__project__owner').get(id=task_worker['id'])
    rejections = TaskWorker.objects.filter(collective_rejection__isnull=False,
                                           task__project__group_id=task_worker_obj.task.project.group_id).count()
    if rejections >= settings.COLLECTIVE_REJECTION_THRESHOLD:
        task_worker_obj.task.project.status = Project.STATUS_CROWD_REJECTED
        task_worker_obj.task.project.save()
        mturk_update_status(project={'id': task_worker_obj.task.project_id})
    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def mturk_disable_hit(project):
    user_id = Project.objects.values('owner').get(id=project['id'])['owner']
    user = User.objects.get(id=user_id)
    provider = get_provider(user)
    if provider is None:
        return
    hits = MTurkHIT.objects.filter(task__project__group_id=project['id'])
    for hit in hits:
        provider.disable_hit(hit.hit_id)
        hit.status = MTurkHIT.STATUS_DELETED
        hit.save()
    return 'SUCCESS'


def get_provider(user, host=None):
    if not hasattr(user, 'mturk_account'):
        return None
    if host is None:
        host = SITE_HOST
    client_secret = AESUtil(key=AWS_DAEMO_KEY).decrypt(user.mturk_account.client_secret)
    return MTurkProvider(host=host, aws_access_key_id=user.mturk_account.client_id,
                         aws_secret_access_key=client_secret)


def calculate_cumulative_ratings(owner_id, project_id):
    import numpy as np
    from fancyimpute import SoftImpute, IterativeSVD
    from sklearn.preprocessing import MinMaxScaler

    ROW_WISE = 1
    # COL_WISE = 0

    scaler_top = MinMaxScaler(feature_range=(2, 3))
    scaler_bottom = MinMaxScaler(feature_range=(1, 2))

    # input format: worker_id, task_id, accuracy
    # output format: pivot table of worker_id and task_id with accuracy values
    query = '''
        SELECT
            r.id,
            r.target_id AS worker_id,
            u.username username,
            r.task_id AS task_id,
            weight AS accuracy
        FROM crowdsourcing_rating r
        INNER JOIN crowdsourcing_task t
            ON t.id = r.task_id
        INNER JOIN crowdsourcing_project p
            ON p.id = t.project_id
        INNER JOIN crowdsourcing_taskworker tw
            ON t.id = tw.task_id
                AND tw.worker_id=r.target_id
        INNER JOIN auth_user u ON u.id = r.target_id
        WHERE
            p.group_id = (%(project_id)s)
            AND origin_type=(%(origin_type)s);
    '''

    cursor = connection.cursor()
    cursor.execute(query, {
        'project_id': project_id,
        'origin_type': Rating.RATING_REQUESTER,
        'origin_id': owner_id
    })

    worker_ratings_raw = cursor.fetchall()

    # 0 - rating id
    # 1 - worker_id
    # 2 - username
    # 3 - task_id
    # 4 - accuracy
    d = [{
         'worker_id': worker_rating[1],
         'task_id': worker_rating[3],
         'accuracy': worker_rating[4],
         } for worker_rating in worker_ratings_raw]

    usernames = {}
    for rating in worker_ratings_raw:
        usernames['%d' % rating[1]] = rating[2]

    df = DataFrame(d)

    pivoted = pivot_table(df, values='accuracy', index=['worker_id'], columns=['task_id'])
    pivoted = pivoted.reset_index('worker_id')
    pivoted.index.name = None

    # COLUMNS = ["worker_id", "score", "accuracy", "attempted", "correct", "boomerang"]

    data = pivoted.copy(deep=True)
    matrix = data.ix[:, 1:]  # without worker_id

    # data['accuracy'] = matrix.mean(axis=ROW_WISE) * 100
    # data['attempted'] = matrix.count(axis=ROW_WISE)
    # data['correct'] = matrix.sum(axis=ROW_WISE)

    # data = data[data["attempted"]>=MIN_TASKS]

    # turn incorrect to -1 as imputations will fill with 0
    # matrix[matrix <= 0] = -1

    try:
        mat = IterativeSVD(verbose=False, init_fill_method="mean").complete(matrix)
    except Exception:
        mat = SoftImpute(verbose=False, init_fill_method="mean").complete(matrix)

    data['score'] = mat.mean(axis=ROW_WISE)
    data = data.sort_values(by=['score'], ascending=[False])

    percentile = data['score'].quantile(settings.WORKER_SPLIT_PERCENTILE)

    # Top 25% = 3-2 and Bottom 75% = 2-1
    num_workers = len(data)
    num_workers_top_x = len(data[data['score'] >= percentile])

    top_x = data.head(num_workers_top_x)

    # add extra worker at inflexion point from top set as it will have 2.0 duplicated
    bottom_y = data.tail(num_workers - num_workers_top_x + 1)

    # accuracy = sum(data['correct']) * 100 / sum(data['attempted'])

    top_x_score = scaler_top.fit_transform(np.array(top_x['score']).reshape((len(top_x['score']), 1)))
    bottom_y_score = scaler_bottom.fit_transform(np.array(bottom_y['score']).reshape((len(bottom_y['score']), 1)))

    # ignore the 1st value of bottom list as it is duplicate one from top list.
    boomerang_scores = np.append(top_x_score, bottom_y_score[1:])

    data['boomerang'] = boomerang_scores

    boomerang_ratings = data.to_dict('records')

    worker_ratings = [{"worker_id": r.worker_id, "worker_username": usernames[r.worker_id], "task_avg": r.boomerang,
                       "requester_avg": 0} for r in boomerang_ratings]

    return worker_ratings


@celery_app.task(ignore_result=True)
def update_worker_boomerang(owner_id, project_id):
    # TODO fix group_id
    # noinspection SqlResolve
    # query = '''
    #     SELECT
    #       t.target_id target_id,
    #       t.username username,
    #       t.task_w_avg task_avg,
    #       r.requester_w_avg requester_avg
    #     FROM (
    #            SELECT
    #              target_id,
    #              username,
    #              sum(weight * power((%(BOOMERANG_TASK_ALPHA)s), t.row_number))
    #                / sum(power((%(BOOMERANG_TASK_ALPHA)s), t.row_number)) task_w_avg
    #            FROM (
    #
    #                   SELECT
    #                     r.id,
    #                     u.username username,
    #                     weight,
    #                     r.target_id,
    #                     -1 + row_number()
    #                     OVER (PARTITION BY target_id
    #                       ORDER BY tw.created_at DESC) AS row_number
    #
    #                   FROM crowdsourcing_rating r
    #                     INNER JOIN crowdsourcing_task t ON t.id = r.task_id
    #                     INNER JOIN crowdsourcing_project p ON p.id = t.project_id
    #                     INNER JOIN crowdsourcing_taskworker tw ON t.id = tw.task_id
    #                       AND tw.worker_id=r.target_id
    #                     INNER JOIN auth_user u ON u.id = r.target_id
    #                   WHERE p.group_id = (%(project_id)s) AND origin_type=(%(origin_type)s)) t
    #            GROUP BY target_id, username) t
    #       INNER JOIN
    #       (SELECT
    #          target_id,
    #          username,
    #          sum(weight * power((%(BOOMERANG_REQUESTER_ALPHA)s), r.row_number))
    #            / sum(power((%(BOOMERANG_REQUESTER_ALPHA)s), r.row_number)) requester_w_avg
    #        FROM (
    #
    #               SELECT
    #                 r.id,
    #                 u.username username,
    #                 weight,
    #                 r.target_id,
    #                 -1 + row_number()
    #                 OVER (PARTITION BY target_id
    #                   ORDER BY tw.created_at DESC) AS row_number
    #
    #               FROM crowdsourcing_rating r
    #                 INNER JOIN crowdsourcing_task t ON t.id = r.task_id
    #                 INNER JOIN crowdsourcing_taskworker tw ON t.id = tw.task_id
    #                   AND tw.worker_id=r.target_id
    #                 INNER JOIN auth_user u ON u.id = r.target_id
    #               WHERE origin_id=(%(origin_id)s) AND origin_type=(%(origin_type)s)
    #             ) r
    #        GROUP BY target_id, username) r ON r.target_id = t.target_id;
    # '''

    # cursor = connection.cursor()
    # cursor.execute(query, {'project_id': project_id, 'origin_type': Rating.RATING_REQUESTER, 'origin_id': owner_id,
    #                        'BOOMERANG_REQUESTER_ALPHA': settings.BOOMERANG_REQUESTER_ALPHA,
    #                        'BOOMERANG_TASK_ALPHA': settings.BOOMERANG_TASK_ALPHA})
    #
    # worker_ratings_raw = cursor.fetchall()

    # worker_ratings = [{"worker_id": r[0], "worker_username": r[1], "task_avg": r[2], "requester_avg": r[3]} for r in
    #                   worker_ratings_raw]

    # for rating in worker_ratings:
    #     update_worker_boomerang.delay(project_id, worker_id=rating['worker_id'], task_avg=rating['task_avg'])
    return 'NOT_IMPLEMENTED'
    worker_ratings = calculate_cumulative_ratings(owner_id=owner_id, project_id=project_id)

    user = User.objects.get(id=owner_id)
    provider = get_provider(user=user)

    for rating in worker_ratings:
        user_name = rating["worker_username"].split('.')
        if len(user_name) == 2 and user_name[0] == 'mturk':
            mturk_worker_id = user_name[1].upper()
            provider.update_worker_boomerang(project_id, worker_id=mturk_worker_id, task_avg=rating['task_avg'],
                                             requester_avg=rating['requester_avg'])

    return 'SUCCESS'


@celery_app.task(ignore_result=True)
def expire_hits():
    # noinspection SqlResolve
    query = '''
        WITH assignments AS (
            SELECT
              ma.id assignment_id,
              ma.status
            FROM crowdsourcing_taskworker tw
              INNER JOIN mturk_mturkassignment ma ON ma.task_worker_id = tw.id
            WHERE tw.status = (%(expired)s) AND ma.status <> tw.status
        )
        UPDATE mturk_mturkassignment SET status=(%(expired)s) FROM assignments
        WHERE assignments.assignment_id=id;
    '''
    cursor = connection.cursor()
    cursor.execute(query, {'expired': TaskWorker.STATUS_EXPIRED})

    return 'SUCCESS'
