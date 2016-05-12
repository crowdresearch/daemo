from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.models import Qualification, QualificationItem


class QualificationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Qualification
        fields = ('id', 'name', 'description')

    def create(self, owner, *args, **kwargs):
        return Qualification.objects.create(owner=owner, **self.validated_data)


class QualificationItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = QualificationItem
        fields = ('id', 'expression')

    def create(self, qualification, *args, **kwargs):
        return QualificationItem.objects.create(qualification_id=qualification, **self.validated_data)
