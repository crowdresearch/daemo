__author__ = 'dmorina'
from crowdsourcing.serializers.requester import *
from rest_framework import generics

class Requester(generics.ListCreateAPIView):
    from crowdsourcing.models import Requester
    queryset = Requester.objects.all()
    serializer_class = RequesterSerializer

class RequesterRanking(generics.ListCreateAPIView):
    from crowdsourcing.models import RequesterRanking
    queryset = RequesterRanking.objects.all()
    serializer_class = RequesterRankingSerializer
