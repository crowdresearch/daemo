from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rest_framework import status, viewsets, serializers, mixins
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.models import Rating, TaskWorker, Project, RawRatingFeedback, Match
from crowdsourcing.permissions.rating import IsRatingOwner
from crowdsourcing.serializers.rating import RatingSerializer
from crowdsourcing.utils import get_pk
from mturk.tasks import update_worker_boomerang


class RatingViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, IsRatingOwner]

    def create(self, request, *args, **kwargs):
        worker = request.data.get('target')
        target = User.objects.filter(profile__handle=worker).first()
        if target is None:
            return Response({"message": "User with handle {} not found!".format(worker)},
                            status=status.HTTP_404_NOT_FOUND)
        origin_type = request.data.get('origin_type', Rating.RATING_REQUESTER)
        if target.id == request.user.id:
            return Response({"message": "Cannot rate self!"}, status=status.HTTP_400_BAD_REQUEST)
        if origin_type == 'worker':
            origin_type = Rating.RATING_WORKER
        elif origin_type == 'requester':
            origin_type = Rating.RATING_REQUESTER

        serializer = RatingSerializer(
            data={"origin_type": origin_type, "target": target.id, "weight": request.data.get('weight')})
        if serializer.is_valid():
            rating = serializer.create(origin=request.user)
            return Response({"id": rating.id}, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @staticmethod
    def get_true_skill_ratings(match_group_id):
        ratings = []
        matches = Match.objects.filter(group=match_group_id)
        for match in matches:
            workers = match.workers.all()
            for worker in workers:
                rating = {
                    "task_id": worker.task_worker.task_id,
                    "worker_id": worker.task_worker.worker_id,
                    "weight": worker.mu
                }
                ratings.append(rating)
        return ratings

    @list_route(methods=['get'], url_path='trueskill')
    def true_skill(self, request, *args, **kwargs):
        match_group_id = request.query_params.get('match_group_id', -1)
        ratings = self.get_true_skill_ratings(match_group_id)
        return Response(status=status.HTTP_200_OK, data=ratings)

    @list_route(methods=['post'], url_path='boomerang-feedback')
    def boomerang_feedback(self, request, *args, **kwargs):
        origin_id = request.user.id
        id_or_hash = request.data.get('project_key', -1)
        ignore_history = request.data.get('ignore_history', False)
        project_group_id, is_hash = get_pk(id_or_hash)
        # project_id = project_group_id
        # if is_hash:
        #     project_id = Project.objects.filter(group_id=project_group_id).order_by('-id').first().id
        origin_type = Rating.RATING_REQUESTER
        ratings = request.data.get('ratings', [])
        task_ids = [r['task_id'] for r in ratings]
        worker_ids = [r['worker_id'] for r in ratings]
        task_workers = TaskWorker.objects.filter(
            Q(status__in=[TaskWorker.STATUS_ACCEPTED, TaskWorker.STATUS_SUBMITTED]),
            task__project__owner_id=origin_id,
            task__project__group_id=project_group_id,
            task_id__in=task_ids, worker_id__in=worker_ids)
        if task_workers.count() != len(ratings):
            raise serializers.ValidationError(
                detail={"message": "Task worker ids are not valid, or do not belong to this project"})
        raw_ratings = []
        for r in ratings:
            raw_ratings.append(RawRatingFeedback(requester_id=origin_id, worker_id=r['worker_id'], weight=r['weight'],
                                                 task_id=r['task_id']))
        with transaction.atomic():
            RawRatingFeedback.objects.filter(task_id__in=task_ids, worker_id__in=worker_ids,
                                             requester_id=origin_id).delete()
            RawRatingFeedback.objects.filter(requester_id=origin_id, task__project__group_id=project_group_id).update(
                is_excluded=ignore_history)
            RawRatingFeedback.objects.bulk_create(raw_ratings)

            raw_ratings_obj = RawRatingFeedback.objects.filter(requester_id=origin_id,
                                                               task__project__group_id=project_group_id,
                                                               is_excluded=False)

            all_ratings = [{"weight": rr.weight, "worker_id": rr.worker_id, "task_id": rr.task_id} for rr in
                           raw_ratings_obj]
            all_worker_ids = [rr.worker_id for rr in raw_ratings_obj]
            min_val = min([r['weight'] for r in all_ratings])
            max_val = max([r['weight'] for r in all_ratings]) - min_val

            rating_objects = []

            for rating in all_ratings:
                rating['weight'] = 1 + (round(float(rating['weight'] -
                                                    min_val) / max_val, 2) * 2) if max_val != 0 else 2.0
                rating_objects.append(
                    Rating(origin_type=origin_type, origin_id=origin_id, target_id=rating['worker_id'],
                           task_id=rating['task_id'], weight=rating['weight']))

            Rating.objects.filter(origin_type=origin_type, origin_id=origin_id, target_id__in=all_worker_ids,
                                  task__project__group_id=project_group_id).delete()
            Rating.objects.bulk_create(rating_objects)

        update_worker_boomerang.delay(origin_id, project_group_id)

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

    @list_route(methods=['post'], url_path='by-project')
    def by_project(self, request, *args, **kwargs):
        project_id = request.data.get('project')
        origin_type = request.data.get('origin_type', Rating.RATING_REQUESTER)
        target = request.data.get('target')
        weight = request.data.get('weight')
        origin = request.user.id
        if origin_type == Rating.RATING_REQUESTER:
            project = Project.objects.filter(id=project_id, owner=request.user).first()
            worker_id = target
        else:
            project = Project.objects.filter(id=project_id, owner=target).first()
            worker_id = origin
        if project_id is None or project is None:
            return Response({"message": "Invalid project id provided"}, status=status.HTTP_400_BAD_REQUEST)

        tasks = TaskWorker.objects.filter(status__in=[1, 2, 3, 5], worker_id=worker_id,
                                          task__project__group_id=project.group_id).values_list('task_id', flat=True)
        rating_objects = []
        for t in tasks:
            rating_objects.append(
                Rating(target_id=target, origin_id=origin, task_id=t, weight=weight, origin_type=origin_type))
        Rating.objects.filter(target_id=target, origin_id=origin, task__in=tasks, origin_type=origin_type).delete()
        Rating.objects.bulk_create(rating_objects)
        return Response({"message": "Ratings saved successfully"})
