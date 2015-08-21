from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from crowdsourcing.serializers.requesterinputfile import RequesterInputFileSerializer
from crowdsourcing.models import RequesterInputFile


class FileManagerViewSet(ViewSet):
    queryset = RequesterInputFile.objects.filter(deleted=False)
    serializer_class = RequesterInputFileSerializer

    # just upload file and return id
    def create(self, request, *args, **kwargs):
        uploadedFile = request.data['file']
        serializer = RequesterInputFileSerializer(data=request.data)
        if serializer.is_valid():
            resp = serializer.create()
            return Response(resp)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # delete uploaded file and database record
    def destroy(self, request, *args, **kwargs):
        serializer = RequesterInputFileSerializer()
        queryset = RequesterInputFile.objects.filter(id=kwargs['pk'])
        serializer.delete_file_and_instance(queryset)
        return Response({'status': 'deleted'})

