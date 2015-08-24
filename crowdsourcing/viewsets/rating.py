from crowdsourcing.serializers.requester import RequesterSerializer
from crowdsourcing.serializers.user import UserProfileSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from crowdsourcing.models import WorkerRequesterRating
from crowdsourcing.serializers.rating import WorkerRequesterRatingSerializer


class WorkerRequesterRatingViewset(viewsets.ModelViewSet):
    queryset = WorkerRequesterRating.objects.all()
    serializer_class = WorkerRequesterRatingSerializer

    def create(self, request, *args, **kwargs):
        wrr_serializer = WorkerRequesterRatingSerializer(data=request.data)
        if wrr_serializer.is_valid():
            wrr_serializer.create(origin=request.user.userprofile)
            return Response({'status': 'Rating created'})
        else:
            return Response(wrr_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)