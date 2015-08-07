from rest_framework import serializers
from crowdsourcing.models import RequesterInputFile
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer

class RequesterInputFileSerializer(DynamicFieldsModelSerializer):

	class Meta:
		model = RequesterInputFile
		fields = ('id', 'file', 'deleted')
	
	def create(self, **kwargs):
		uploadedFile = self.validated_data['file']
		f = RequesterInputFile(deleted=False, file=uploadedFile)
		f.save()
		return f.id