from django.db import transaction
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.models import WebHook
from crowdsourcing.permissions.util import IsOwnerOrReadOnly
from crowdsourcing.serializers.webhooks import WebHookSerializer


class WebHookViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = WebHook.objects.all()
    serializer_class = WebHookSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    @list_route(methods=['get'], url_path='spec')
    def spec(self, request, *args, **kwargs):
        return Response([s for s in self.queryset.model.SPEC if s['is_active']])

    def list(self, request, *args, **kwargs):
        return Response(self.serializer_class(instance=request.user.web_hooks.all(), many=True).data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.create(serializer.validated_data, owner=request.user)
            return Response({"id": instance.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.update(instance, serializer.validated_data)
            return Response({"id": instance.id}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
