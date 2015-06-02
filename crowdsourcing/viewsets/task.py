__author__ = 'elsabakiu, dmorina, asmita, megha'

from crowdsourcing.serializers.task import *
from rest_framework import viewsets

class TaskViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Task
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class CurrencyViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Currency
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer