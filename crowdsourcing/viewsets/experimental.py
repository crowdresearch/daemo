from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from crowdsourcing.serializers.experimental import TaskRankingSerializer
from crowdsourcing.experimental_models import TaskRanking


class TaskRankingViewSet(viewsets.ModelViewSet):
    queryset = TaskRanking.objects.all()
    serializer_class = TaskRankingSerializer
    permission_classes = [IsAuthenticated]