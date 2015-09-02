from crowdsourcing.serializers.project import ProjectSerializer, ModuleSerializer
from crowdsourcing.serializers.requester import RequesterSerializer
from crowdsourcing.serializers.task import TaskWorkerSerializer
from crowdsourcing.serializers.user import UserProfileSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from crowdsourcing.models import WorkerRequesterRating, Module, Task, TaskWorker, Worker, Project
from crowdsourcing.serializers.rating import WorkerRequesterRatingSerializer


class WorkerRequesterRatingViewset(viewsets.ModelViewSet):
    queryset = WorkerRequesterRating.objects.all()
    serializer_class = WorkerRequesterRatingSerializer

    def create(self, request, *args, **kwargs):
        wrr_serializer = WorkerRequesterRatingSerializer(data=request.data)
        if wrr_serializer.is_valid():
            wrr_serializer.create(origin=request.user.userprofile)
            return Response({'status': 'Rating created'})
        else:
            return Response(wrr_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        wrr_serializer = WorkerRequesterRatingSerializer(data=request.data, partial=True)
        wrr = self.get_object()
        if wrr_serializer.is_valid():
            wrr_serializer.update(wrr, wrr_serializer.validated_data)

            return Response({'status': 'updated rating'})
        else:
            return Response(wrr_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

class RatingViewset(viewsets.ModelViewSet):
    queryset = Project.objects.filter(deleted=False)
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    @list_route(methods=['GET'])
    def workers_reviews(self, request, **kwargs):

        from django.db.models import Count
        data = TaskWorker.objects.values('task__module__name', 'task__module__id',
            'worker__profile__rating_target__weight', 'worker__profile__id','worker__alias')\
            .filter(task__module__project__owner=request.user.userprofile.requester.id, task_status__in=[3,4,5]).extra(
            where=["(crowdsourcing_module.id=crowdsourcing_workerrequesterrating.module_id OR crowdsourcing_workerrequesterrating.module_id is null)"]
            ).annotate(task_count=Count('task'))

        pending_reviews = {}
        modules = set([])
        for entry in data:
          pending_reviews[(entry["task__module__id"], entry["worker__profile__id"])] = entry
          modules.add(entry["task__module__id"])

        # Get existing ratings
        ratings = WorkerRequesterRating.objects.all().filter(
          origin=request.user.userprofile, module__in=modules, origin_type="requester")
        rating_map = {}
        for rating in ratings:
          rating_map[(rating.module.id, rating.target.id)] = rating

        for key, val in rating_map.items():
          if key in pending_reviews:
            current_review = pending_reviews[key]
            current_review["current_rating"] = val.weight
            current_review["current_rating_id"] = val.id

        response = []
        for review in pending_reviews.values():
          row = {
            "module_name": review["task__module__name"],
            "module_id": review["task__module__id"],
            "worker_alias": review["worker__alias"],
            "task_count": review["task_count"],
            "worker_profile_id": review["worker__profile__id"]
          }
          if "current_rating_id" in review and "current_rating" in review:
            row["current_rating"] = review["current_rating"]
            row["current_rating_id"] = review["current_rating_id"]
          response.append(row)

        return Response(response)


    @list_route(methods=['GET'])
    def requesters_reviews(self, request, **kwargs):
        task_workers = TaskWorker.objects.all().filter(
          worker=request.user.userprofile.worker, task_status__in=[2, 3, 4, 5])
        modules = []
        pending_reviews = {}

        for task_worker in task_workers:
          module = task_worker.task.module
          modules.append(module)
          pending_reviews[(module.id, module.project.owner.profile.user.id)] = {
            "task_worker": TaskWorkerSerializer(instance=task_worker).data,
            "project_owner_alias": module.project.owner.profile.user.username,
            "project_name": module.project.name,
            "target": module.project.owner.profile.user.id,
            "module": module.id,
            "module_name": module.name
          }

        # Get existing ratings
        ratings = WorkerRequesterRating.objects.all().filter(
          origin=request.user.userprofile, module__in=modules, origin_type="worker")
        rating_map = {}
        for rating in ratings:
          rating_map[(rating.module.id, rating.target.id)] = rating

        for key, val in rating_map.items():
          if key in pending_reviews:
            current_review = pending_reviews[key]
            current_review["current_rating"] = val.weight
            current_review["current_rating_id"] = val.id

        return Response(pending_reviews.values())