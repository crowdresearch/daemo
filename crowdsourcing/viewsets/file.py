from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from crowdsourcing.serializers.file import FileSerializer
from crowdsourcing.models import File
import csv

class FileViewSet(ViewSet):
	queryset = File.objects.filter(deleted=False)
	serializer_class = FileSerializer

	def get_metadata(self, request, *args, **kwargs):
		uploadedFile = request.data['file']
		csvinput = csv.reader(uploadedFile)
		column_headers = csvinput.next()
		num_rows = sum(1 for row in csvinput)
		file_serializer = FileSerializer(data=request.data)
		if file_serializer.is_valid():
			id = file_serializer.create()
			metadata = {'id': id, 'num_rows': num_rows, 'column_headers': column_headers}
			return Response({'metadata': metadata})
		else:
			return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def destroy(self, request, *args, **kwargs):
		file_serializer = FileSerializer()
		file = self.get_object()
		file_serializer.delete(file)
		return Response({'status': 'deleted file'})

	def parse(self, request):
		uploadedFile = request.data['file']
		csvinput = csv.DictReader(uploadedFile)
		arr = []
		for row in csvinput:
			arr.append(row)
		return Response(arr)