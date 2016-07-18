from itertools import groupby
from operator import itemgetter

from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.serializers.project import ProjectSerializer
from crowdsourcing.models import Rating, TaskWorker, Project
from crowdsourcing.serializers.rating import RatingSerializer
from crowdsourcing.permissions.rating import IsRatingOwner
from mturk.tasks import update_worker_boomerang


class WorkerRequesterRatingViewset(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, IsRatingOwner]

    def create(self, request, *args, **kwargs):
        wrr_serializer = RatingSerializer(data=request.data)
        if wrr_serializer.is_valid():
            wrr = wrr_serializer.create(origin=request.user)
            wrr_serializer = RatingSerializer(instance=wrr)
            if wrr.origin_type == Rating.RATING_REQUESTER:
                update_worker_boomerang.delay(wrr.origin_id, wrr.project_id, wrr.target_id, wrr.weight)
            return Response(wrr_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(wrr_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        wrr_serializer = RatingSerializer(data=request.data, partial=True)
        wrr = self.get_object()
        if wrr_serializer.is_valid():
            wrr = wrr_serializer.update(wrr, wrr_serializer.validated_data)
            wrr_serializer = RatingSerializer(instance=wrr)
            if wrr.origin_type == Rating.RATING_REQUESTER:
                update_worker_boomerang.delay(wrr.origin_id, wrr.project_id, wrr.target_id, wrr.weight)
            return Response(wrr_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(wrr_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'], url_path='boomerang-feedback')
    def boomerang_feedback(self, request, *args, **kwargs):
        origin_id = request.user.id
        project_id = request.data.get('project_id', -1)
        origin_type = Rating.RATING_REQUESTER
        ratings = request.data.get('ratings', [])
        task_worker_ids = [r['task_worker'] for r in ratings]
        task_workers = TaskWorker.objects.filter(task__project__owner_id=origin_id,
                                                 task__project_id=project_id,
                                                 id__in=task_worker_ids)
        if task_workers.count() != len(ratings):
            return Response(data={"message": "Task worker ids are not valid, or do not belong to this project"})
        group_func = itemgetter('worker_id')
        ratings_grouped = groupby(ratings, group_func)
        max_val = max([r['weight'] for r in ratings_grouped])
        rating_objects = []
        for rating in ratings_grouped:
            rating['weight'] = 1 + (round(float(rating['weight']) / max_val, 2) * 2)
            rating_objects.append(Rating(origin_type=origin_type, origin_id=origin_id, target_id=rating['worker_id'],
                                         project_id=project_id, weight=rating['weight']))
        Rating.objects.bulk_create(rating_objects)
        for rating in ratings_grouped:
            update_worker_boomerang.delay(origin_id, project_id, rating['worker_id'], rating['weight'])

        return Response(data={"message": "Success"}, status=status.HTTP_201_CREATED)

    @list_route(methods=['get'], url_path='list-by-target')
    def list_by_target(self, request, *args, **kwargs):
        origin_type = request.query_params.get('origin_type')
        origin_type = 1 if origin_type == 'worker' else 2

        target = request.query_params.get('target', -1)
        rating = Rating.objects.values('id', 'weight') \
            .filter(origin_id=request.user.id, target_id=target, origin_type=origin_type) \
            .order_by('-updated_at').first()
        if rating is None:
            rating = {
                'id': None,
            }
        rating.update({'target': target})
        rating.update({'origin_type': origin_type})
        return Response(data=rating, status=status.HTTP_200_OK)


class RatingViewset(viewsets.ModelViewSet):
    queryset = Project.objects.filter(deleted_at__isnull=True)
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    @list_route(methods=['GET'])
    def workers_ratings_by_project(self, request, **kwargs):
        project_id = request.query_params.get('project', -1)
        # noinspection SqlResolve
        data = TaskWorker.objects.raw(
            '''
               SELECT
                  r.id                 id,
                  2                    origin_type,
                  r.weight             weight,
                  u.id                 target,
                  u.username           username,
                  p.owner_id           origin,
                  COUNT(tw.task_id) AS "task_count"
                FROM crowdsourcing_taskworker tw
                  INNER JOIN crowdsourcing_task t ON (tw.task_id = t.id)
                  INNER JOIN crowdsourcing_project p
                    ON (t.project_id = p.id)
                  INNER JOIN auth_user u
                    ON (u.id = p.owner_id)
                  LEFT OUTER JOIN crowdsourcing_rating r
                    ON (u.id = r.target_id)
                WHERE (tw.status IN (3, 4, 5) AND o.id = %s)
                GROUP BY
                  r.weight,
                  p.owner_id,
                  r.id
                ORDER BY "task_count" DESC, username;
            ''', params=[project_id]
        )

        serializer = RatingSerializer(data, many=True, context={'request': request})
        response_data = serializer.data
        return Response(data=response_data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def requesters_ratings(self, request, **kwargs):
        data = TaskWorker.objects.raw(
            '''
                SELECT
                  DISTINCT
                  (u.username)  username,
                  1             origin_type,
                %(worker)s      origin,
                r.id            id,
                u.id            target,
                r.weight        weight
                FROM crowdsourcing_taskworker tw
                INNER JOIN crowdsourcing_task t ON tw.task_id=t.id
                INNER JOIN crowdsourcing_project p ON t.project_id=p.id
                INNER JOIN auth_user u ON p.owner_id=u.id
                LEFT OUTER JOIN crowdsourcing_rating r ON u.id=r.target_id
                WHERE tw.status IN (3, 4, 5) AND tw.worker_id=%(worker)s;
            ''', params={'worker': request.user.id}
        )
        serializer = RatingSerializer(data, many=True, context={'request': request})
        response_data = serializer.data
        return Response(data=response_data, status=status.HTTP_200_OK)
