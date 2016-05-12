from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.models import Qualification, QualificationItem
from crowdsourcing.serializers.qualification import QualificationSerializer, QualificationItemSerializer


class QualificationViewSet(viewsets.ModelViewSet):
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer
    permission_classes = [IsAuthenticated]
    item_queryset = QualificationItem.objects.all()
    item_serializer_class = QualificationItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.create(owner=request.user.userprofile.requester)
            return Response(data={"message": "Successfully created"}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(owner=request.user.userprofile.requester)
        serializer = self.serializer_class(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='create-item')
    def create_item(self, request, pk=None, *args, **kwargs):
        serializer = self.item_serializer_class(data=request.data)
        if serializer.is_valid():
            item = serializer.create(qualification=pk)
            return Response({'id': item.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], url_path='list-items')
    def list_items(self, request, pk=None, *args, **kwargs):
        queryset = self.item_queryset.filter(qualification_id=pk)
        serializer = self.item_serializer_class(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QualificationItemViewSet(viewsets.ModelViewSet):
    queryset = QualificationItem.objects.all()
    serializer_class = QualificationItemSerializer
