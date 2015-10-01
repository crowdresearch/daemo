from rest_framework import serializers


class WorkerProjectsSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    module_id = serializers.ReadOnlyField()
    project_id = serializers.ReadOnlyField()
    requester_id = serializers.ReadOnlyField()
    requester_name = serializers.ReadOnlyField()
    project_name = serializers.ReadOnlyField()
    module_name = serializers.ReadOnlyField()
    module_description = serializers.ReadOnlyField()
    task_time_minutes = serializers.ReadOnlyField()
    rank = serializers.ReadOnlyField()