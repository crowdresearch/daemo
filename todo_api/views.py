from rest_framework import generics
import serializers
import models


class TodoListItemsCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.TodoListItemSerializer
    queryset = models.TodoListItem.objects.all()


class TodoInstanceView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.TodoListItemSerializer
    queryset = models.TodoListItem.objects.all()
