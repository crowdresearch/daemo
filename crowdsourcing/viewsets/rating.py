from crowdsourcing.serializers.requester import *
from crowdsourcing.serializers.project import *
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from crowdsourcing.models import WorkerRequesterRating
from crowdsourcing.serializers.rating import WorkerRequesterRatingSerializer


class WorkerRequesterRatingViewset(viewsets.ModelViewSet):
    queryset = WorkerRequesterRating.objects.all()
    serializer_class = WorkerRequesterRatingSerializer