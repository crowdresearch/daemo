from crowdsourcing.serializers.requester import *
from crowdsourcing.serializers.project import *
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from crowdsourcing.models import WorkerRequesterRating
from crowdsourcing.serializers.rating import WorkerRequesterRatingSerializer


class WorkerRequesterRatingViewset(viewsets.ModelViewSet):
    queryset = WorkerRequesterRating.objects.all()
    serializer_class = WorkerRequesterRatingSerializer

    @detail_route(methods=['post'])
    def update_workerrequestrating(self, request, id=None):
        wrrating_serializer = WorkerRequesterRatingSerializer(data = request.data)
        wrrating = self.get_object()
        if wrrating_serializer.is_valid():
            wrrating_serializer.update(wrrating, wrrating_serializer.validated_data)

            return Response({'status': 'updated'})
        else:
            return Response(wrrating_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)