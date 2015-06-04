__author__ = 'dmorina, asmita, megha'

from crowdsourcing.serializers.requester import *
from rest_framework import viewsets

class RequesterViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Requester
    queryset = Requester.objects.all()
    serializer_class = RequesterSerializer


class RequesterRankingViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import RequesterRanking
    queryset = RequesterRanking.objects.all()
    serializer_class = RequesterRankingSerializer


class QualificationViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Qualification
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer