from crowdsourcing import models
from rest_framework import serializers
from crowdsourcing.models import File
from crowdsourcing.serializers.file import File
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer

class FileSerializer(DynamicFieldsModelSerializer):

	class Meta:
		model = models.File
		fields = ('id', 'file', 'deleted')
	
	def create(self, **kwargs):
		uploadedFile = self.validated_data['file']
		f = File(deleted=False, file=uploadedFile)
		f.save()
		return f.id

	def delete(self, instance):
		instance.deleted = True
		instance.save()
		return instance