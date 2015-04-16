from rest_framework import serializers
import models


class TodoListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TodoListItem
