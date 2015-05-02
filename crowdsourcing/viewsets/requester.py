__author__ = 'dmorina'
from crowdsourcing.serializers.requester import *
from rest_framework import generics
from rest_framework import status, views as rest_framework_views, viewsets

class RequesterViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Requester
    queryset = Requester.objects.all()
    serializer_class = RequesterSerializer

class RequesterRankingViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import RequesterRanking
    queryset = RequesterRanking.objects.all()
    serializer_class = RequesterRankingSerializer
