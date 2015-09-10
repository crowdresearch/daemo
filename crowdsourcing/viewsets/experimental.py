from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from crowdsourcing.serializers.experimental import TaskRankingSerializer
from crowdsourcing.experimental_models import TaskRanking
from crowdsourcing.permissions.experimental import IsTaskWorker
from crowdsourcing.permissions.user import IsWorker
from rest_framework import mixins


class TaskRankingViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = TaskRanking.objects.all()
    serializer_class = TaskRankingSerializer
    permission_classes = [IsAuthenticated, IsWorker, IsTaskWorker]
    lookup_field = 'task'
