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
        projects = request.user.userprofile.requester.project_owner.all()
        modules = Module.objects.all().filter(project__in=projects)
        tasks = []
        module_task_map = {}
        for module in modules:
          module_tasks = Task.objects.all().filter(module=module)
          for tsk in module_tasks:
            module_task_map[tsk.id] = tsk.module
          tasks.extend(module_tasks)
        task_workers = TaskWorker.objects.all().filter(
            task__in=tasks, task_status__in=[2, 3, 4, 5])
        serializer = TaskWorkerSerializer(instance=task_workers, many=True)
        for entry in serializer.data:
          entry["module"] = module_task_map[entry["task"]].id
          entry["module_name"] = module_task_map[entry["task"]].name
          entry["target"] = entry["worker"]

        #dedupe by module and worker
        pending_reviews = {}
        for entry in serializer.data:
          pending_reviews[(entry["module"], entry["worker"])] = entry

        # Get existing ratings
        ratings = WorkerRequesterRating.objects.all().filter(
          origin=request.user.userprofile, module__in=modules, type="requester")
        rating_map = {}
        for rating in ratings:
          rating_map[(rating.module.id, rating.target.id)] = rating

        for key, val in rating_map.items():
          if key in pending_reviews:
            current_review = pending_reviews[key]
            current_review["current_rating"] = val.weight
            current_review["current_rating_id"] = val.id

        return Response(pending_reviews.values())


    @list_route(methods=['GET'])
    def requesters_reviews(self, request, **kwargs):
        worker = Worker.objects.get(profile=request.user.userprofile)
        task_workers = TaskWorker.objects.all().filter(worker=worker, task_status__in=[2, 3, 4, 5])
        modules = []
        pending_reviews = {}

        for task_worker in task_workers:
          module = task_worker.task.module
          modules.append(module)
          pending_reviews[(module.id, module.project.owner.profile.user.id)] = {
            "task_worker": TaskWorkerSerializer(instance=task_worker).data,
            "project": ProjectSerializer(instance=module.project).data,
            "project_owner_alias": module.project.owner.profile.user.username,
            "target": module.project.owner.profile.user.id,
            "module": module.id,
            "module_data": ModuleSerializer(instance=module).data
          }

        # Get existing ratings
        ratings = WorkerRequesterRating.objects.all().filter(
          origin=worker.profile, module__in=modules, type="worker")
        rating_map = {}
        for rating in ratings:
          rating_map[(rating.module.id, rating.target.id)] = rating
        for key, val in rating_map.items():
          if key in pending_reviews:
            current_review = pending_reviews[key]
            current_review["current_rating"] = val.weight
            current_review["current_rating_id"] = val.id

        return Response(pending_reviews.values())