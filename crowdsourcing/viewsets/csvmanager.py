from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
import csv

class CSVManagerViewSet(ViewSet):

    def parse(self, request):
        uploadedFile = request.data['file']
        csvinput = csv.DictReader(uploadedFile)
        arr = []
        for row in csvinput:
            arr.append(row)
        return Response(arr)