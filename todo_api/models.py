from django.db import models


class TodoListItem(models.Model):
    description = models.CharField(max_length=140, null=False)
    done = models.BooleanField(null=False, default=False)
