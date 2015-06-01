class TaskViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Task
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
