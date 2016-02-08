from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.serializers.project import ProjectSerializer
from crowdsourcing.models import WorkerRequesterRating, TaskWorker, Project
from crowdsourcing.serializers.rating import WorkerRequesterRatingSerializer
from crowdsourcing.permissions.rating import IsRatingOwner


class WorkerRequesterRatingViewset(viewsets.ModelViewSet):
    queryset = WorkerRequesterRating.objects.all()
    serializer_class = WorkerRequesterRatingSerializer
    permission_classes = [IsAuthenticated, IsRatingOwner]

    def create(self, request, *args, **kwargs):
        wrr_serializer = WorkerRequesterRatingSerializer(data=request.data)
        if wrr_serializer.is_valid():
            wrr = wrr_serializer.create(origin=request.user.userprofile)
            wrr_serializer = WorkerRequesterRatingSerializer(instance=wrr)
            return Response(wrr_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(wrr_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        wrr_serializer = WorkerRequesterRatingSerializer(data=request.data, partial=True)
        wrr = self.get_object()
        if wrr_serializer.is_valid():
            wrr = wrr_serializer.update(wrr, wrr_serializer.validated_data)
            wrr_serializer = WorkerRequesterRatingSerializer(instance=wrr)
            return Response(wrr_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(wrr_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'], url_path='list-by-target')
    def list_by_target(self, request, *args, **kwargs):
        origin_type = request.query_params.get('origin_type')
        target = request.query_params.get('target', -1)
        rating = WorkerRequesterRating.objects.values('id', 'weight')\
            .filter(origin_id=request.user.userprofile.id, target_id=target, origin_type=origin_type)\
            .order_by('-last_updated').first()
        if rating is None:
            rating = {
                'id': None,
            }
        rating.update({'target': target})
        rating.update({'origin_type': origin_type})
        return Response(data=rating, status=status.HTTP_200_OK)


class RatingViewset(viewsets.ModelViewSet):
    queryset = Project.objects.filter(deleted=False)
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    @list_route(methods=['GET'])
    def workers_ratings_by_project(self, request, **kwargs):
        project_id = request.query_params.get('project', -1)
        data = TaskWorker.objects.raw(
            '''
                SELECT
                  "crowdsourcing_workerrequesterrating"."id" id,
                  'requester' origin_type,
                  "crowdsourcing_workerrequesterrating"."weight" weight,
                  "crowdsourcing_worker"."profile_id" target,
                  "crowdsourcing_worker"."alias" alias,
                  "crowdsourcing_project"."owner_id" origin,
                  COUNT("crowdsourcing_taskworker"."task_id") AS "task_count"
                FROM "crowdsourcing_taskworker"
                  INNER JOIN "crowdsourcing_task" ON ("crowdsourcing_taskworker"."task_id" = "crowdsourcing_task"."id")
                  INNER JOIN "crowdsourcing_project"
                    ON ("crowdsourcing_task"."project_id" = "crowdsourcing_project"."id")
                  INNER JOIN "crowdsourcing_worker"
                  ON ("crowdsourcing_taskworker"."worker_id" = "crowdsourcing_worker"."id")
                  INNER JOIN "crowdsourcing_userprofile"
                  ON ("crowdsourcing_worker"."profile_id" = "crowdsourcing_userprofile"."id")
                  LEFT OUTER JOIN "crowdsourcing_workerrequesterrating"
                    ON ("crowdsourcing_userprofile"."id" = "crowdsourcing_workerrequesterrating"."target_id")
                WHERE ("crowdsourcing_taskworker"."task_status" IN (3, 4, 5) AND "crowdsourcing_project"."id" = %s)
                GROUP BY
                  "crowdsourcing_workerrequesterrating"."weight", "crowdsourcing_worker"."profile_id",
                  "crowdsourcing_worker"."alias", "crowdsourcing_project"."owner_id",
                  "crowdsourcing_workerrequesterrating"."id"
                ORDER BY "task_count" DESC, "alias";
            ''', params=[project_id]
        )

        serializer = WorkerRequesterRatingSerializer(data, many=True, context={'request': request})
        response_data = serializer.data
        return Response(data=response_data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def requesters_ratings(self, request, **kwargs):
        data = TaskWorker.objects.raw(
            '''
                SELECT
                    DISTINCT(r.alias) alias,
                    'worker' origin_type,
                    %(worker_profile)s origin,
                    wrr.id id,
                    r.profile_id target,
                    wrr.weight weight
                FROM crowdsourcing_taskworker tw
                INNER JOIN crowdsourcing_task t ON tw.task_id=t.id
                INNER JOIN crowdsourcing_project p ON t.project_id=p.id
                INNER JOIN crowdsourcing_requester r ON p.owner_id=r.id
                INNER JOIN crowdsourcing_userprofile up ON r.profile_id=up.id
                LEFT OUTER JOIN crowdsourcing_workerrequesterrating wrr ON up.id=wrr.target_id
                WHERE tw.task_status IN (3,4,5) AND tw.worker_id=%(worker)s;
            ''', params={'worker_profile': request.user.userprofile.id, 'worker': request.user.userprofile.worker.id}
        )
        serializer = WorkerRequesterRatingSerializer(data, many=True, context={'request': request})
        response_data = serializer.data
        return Response(data=response_data, status=status.HTTP_200_OK)
