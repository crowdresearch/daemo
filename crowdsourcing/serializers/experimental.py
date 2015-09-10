from rest_framework import serializers
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.experimental_models import TaskRanking


class TaskRankingSerializer(DynamicFieldsModelSerializer):
    worker_alias = serializers.SerializerMethodField()

    class Meta:
        model = TaskRanking
        fields = ('id', 'task', 'worker', 'weight', 'worker_alias')

    def get_worker_alias(self, obj):
        return obj.worker.alias
