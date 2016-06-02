from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.serializers.project import ProjectSerializer
from crowdsourcing.models import Rating, TaskWorker, Project
from crowdsourcing.serializers.rating import RatingSerializer
from crowdsourcing.permissions.rating import IsRatingOwner


class WorkerRequesterRatingViewset(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, IsRatingOwner]

    def create(self, request, *args, **kwargs):
        wrr_serializer = RatingSerializer(data=request.data)
        if wrr_serializer.is_valid():
            wrr = wrr_serializer.create(origin=request.user)
            wrr_serializer = RatingSerializer(instance=wrr)
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
            return Response(wrr_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(wrr_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'], url_path='list-by-target')
    def list_by_target(self, request, *args, **kwargs):
        origin_type = request.query_params.get('origin_type')
        target = request.query_params.get('target', -1)
        rating = Rating.objects.values('id', 'weight') \
            .filter(origin_id=request.user.id, target_id=target, origin_type=origin_type) \
            .order_by('-last_updated').first()
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
                  'requester'          origin_type,
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
                WHERE (tw.task_status IN (3, 4, 5) AND o.id = %s)
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
                  (u.username) username,
                  'worker'     origin_type,
                %(worker)s origin,
                r.id id,
                u.id target,
                r.weight weight
                FROM crowdsourcing_taskworker tw
                INNER JOIN crowdsourcing_task t ON tw.task_id=t.id
                INNER JOIN crowdsourcing_project p ON t.project_id=p.id
                INNER JOIN auth_user u ON p.owner_id=u.id
                LEFT OUTER JOIN crowdsourcing_rating r ON u.id=r.target_id
                WHERE tw.task_status IN (3, 4, 5) AND tw.worker_id=%(worker)s;
            ''', params={'worker': request.user.id}
        )
        serializer = RatingSerializer(data, many=True, context={'request': request})
        response_data = serializer.data
        return Response(data=response_data, status=status.HTTP_200_OK)
