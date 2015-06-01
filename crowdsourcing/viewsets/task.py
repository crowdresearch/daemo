
from crowdsourcing.serializers.task import *
from rest_framework import generics
from rest_framework import status, views as rest_framework_views, viewsets


class TaskViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Task
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    

class QualificationViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Qualification
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer
