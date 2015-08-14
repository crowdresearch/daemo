from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from crowdsourcing.serializers.requesterinputfile import RequesterInputFileSerializer
from crowdsourcing.models import RequesterInputFile
from crowdsourcing.utils import get_delimiter
import pandas as pd

class CSVManagerViewSet(ViewSet):
	queryset = RequesterInputFile.objects.filter(deleted=False)
	serializer_class = RequesterInputFileSerializer

	def get_metadata_and_save(self, request, *args, **kwargs):
		uploadedFile = request.data['file']
		delimiter = get_delimiter(uploadedFile.name)
		df = pd.DataFrame(pd.read_csv(uploadedFile, sep=delimiter))
		column_headers = list(df.columns.values)
		num_rows = len(df.index)
		serializer = RequesterInputFileSerializer(data=request.data)
		if serializer.is_valid():
			id = serializer.create()
			metadata = {'id': id, 'num_rows': num_rows, 'column_headers': column_headers}
			return Response({'metadata': metadata})
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)