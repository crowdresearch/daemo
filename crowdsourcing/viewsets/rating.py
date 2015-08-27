from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from crowdsourcing.models import WorkerRequesterRating
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from crowdsourcing.serializers.rating import WorkerRequesterRatingSerializer
from crowdsourcing.permissions.rating import IsRatingOwnerOrReadOnly


class WorkerRequesterRatingViewSet(viewsets.ModelViewSet):
    queryset = WorkerRequesterRating.objects.all()
    serializer_class = WorkerRequesterRatingSerializer
    permission_classes = [IsAuthenticated, IsRatingOwnerOrReadOnly]