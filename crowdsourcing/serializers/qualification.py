from rest_framework import serializers

from crowdsourcing import constants
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.models import Qualification, QualificationItem, WorkerAccessControlEntry, \
    RequesterAccessControlGroup
from crowdsourcing.tasks import update_worker_cache


class QualificationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Qualification
        fields = ('id', 'name', 'description')

    def create(self, owner, *args, **kwargs):
        return Qualification.objects.create(owner=owner, **self.validated_data)


class QualificationItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = QualificationItem
        fields = ('id', 'expression', 'qualification', 'scope')

    def create(self, *args, **kwargs):
        return QualificationItem.objects.create(**self.validated_data)

    def update(self, *args, **kwargs):
        self.instance.expression = self.validated_data.get('expression', self.instance.expression)
        self.instance.save()
        return self.instance


class RequesterACGSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = RequesterAccessControlGroup
        fields = ('id', 'requester', 'is_global', 'type', 'name')
        read_only_fields = ('requester',)

    def create(self, requester, *args, **kwargs):
        return RequesterAccessControlGroup.objects.create(requester=requester, **self.validated_data)

    def create_with_entries(self, requester, entries, *args, **kwargs):
        group = RequesterAccessControlGroup.objects.create(requester=requester, **self.validated_data)
        for entry in entries:
            d = {
                'group': group.id,
                'worker': entry
            }
            entry_serializer = WorkerACESerializer(data=d)
            if entry_serializer.is_valid():
                entry_serializer.create()

            else:
                raise ValueError('Invalid user ids')
        update_worker_cache(entries, constants.ACTION_GROUP_ADD, value=group.id)
        return group


class WorkerACESerializer(DynamicFieldsModelSerializer):
    handle = serializers.SerializerMethodField()

    class Meta:
        model = WorkerAccessControlEntry
        fields = ('id', 'worker', 'handle', 'group', 'created_at')

    def create(self, *args, **kwargs):
        instance = WorkerAccessControlEntry.objects.create(**self.validated_data)
        update_worker_cache([instance.worker_id], constants.ACTION_GROUP_ADD, value=instance.group_id)
        return instance

    @staticmethod
    def get_handle(obj):
        return obj.worker.profile.handle
