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


class RatingViewset(viewsets.ModelViewSet):
    queryset = Project.objects.filter(deleted=False)
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    @list_route(methods=['GET'])
    def workers_reviews_by_project(self, request, **kwargs):
        project_id = request.query_params.get('project', -1)
        data = TaskWorker.objects.raw(
            '''
                SELECT
                  "crowdsourcing_workerrequesterrating"."id" id,
                  "crowdsourcing_task"."project_id" project,
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
                    ON ("crowdsourcing_userprofile"."id" = "crowdsourcing_workerrequesterrating"."target_id" and
                    crowdsourcing_workerrequesterrating.project_id = crowdsourcing_project.id)
                WHERE ("crowdsourcing_taskworker"."task_status" IN (2, 3, 4, 5) AND "crowdsourcing_project"."id" = %s)
                GROUP BY "crowdsourcing_task"."project_id",
                  "crowdsourcing_workerrequesterrating"."weight", "crowdsourcing_worker"."profile_id",
                  "crowdsourcing_worker"."alias", "crowdsourcing_project"."owner_id",
                  "crowdsourcing_workerrequesterrating"."id";
            ''', params=[project_id]
        )

        serializer = WorkerRequesterRatingSerializer(data, many=True, context={'request': request})
        response_data = serializer.data
        return Response(data=response_data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def requesters_reviews(self, request, **kwargs):
        task_workers = TaskWorker.objects.all().filter(
            worker=request.user.userprofile.worker, task_status__in=[2, 3, 4, 5])
        projects = []
        pending_reviews = {}

        for task_worker in task_workers:
            project = task_worker.task.project
            projects.append(project)
            pending_reviews[(project.id, project.owner.profile_id)] = {
                # "task_worker": TaskWorkerSerializer(instance=task_worker).data,
                "project_owner_alias": project.owner.alias,
                "project_name": project.name,
                "target": project.owner.profile_id,
                "project": project.id
            }

        # Get existing ratings
        ratings = WorkerRequesterRating.objects.all().filter(
            origin=request.user.userprofile, project__in=projects, origin_type="worker")
        rating_map = {}
        for rating in ratings:
            rating_map[(rating.project.id, rating.target.id)] = rating

        for key, val in rating_map.items():
            if key in pending_reviews:
                current_review = pending_reviews[key]
                current_review["current_rating"] = val.weight
                current_review["current_rating_id"] = val.id

        return Response(pending_reviews.values())
