from rest_framework import serializers
from crowdsourcing.models import RequesterInputFile
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from csp import settings
import os

class RequesterInputFileSerializer(DynamicFieldsModelSerializer):

	class Meta:
		model = RequesterInputFile
		fields = ('id', 'file', 'deleted')
	
	def create(self, **kwargs):
		uploadedFile = self.validated_data['file']
		f = RequesterInputFile(deleted=False, file=uploadedFile)
		f.save()
		return f.id

	# delete the file and database record, instead of just setting the deleted flag
	def delete_file_and_instance(self, queryset):
		instance = queryset.get()
		try:
			os.remove(os.path.join(settings.MEDIA_ROOT, instance.file.name))
		except OSError:
			pass
		queryset.delete()
