from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from crowdsourcing import constants
from crowdsourcing.tasks import update_worker_cache

from crowdsourcing.models import Qualification, QualificationItem, \
    WorkerAccessControlEntry, RequesterAccessControlGroup
from crowdsourcing.serializers.qualification import QualificationSerializer, QualificationItemSerializer, \
    WorkerACESerializer, RequesterACGSerializer


class QualificationViewSet(viewsets.ModelViewSet):
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer
    permission_classes = [IsAuthenticated]
    item_queryset = QualificationItem.objects.all()
    item_serializer_class = QualificationItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.create(owner=request.user)
            return Response(data={"id": instance.id}, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(owner=request.user)
        serializer = self.serializer_class(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class QualificationItemViewSet(viewsets.ModelViewSet):
    queryset = QualificationItem.objects.all()
    serializer_class = QualificationItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            item = serializer.create()
            return Response(data=self.serializer_class(instance=item).data, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            item = serializer.update()
            return Response(data=self.serializer_class(instance=item).data, status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(qualification_id=request.query_params.get('qualification', -1))
        serializer = self.serializer_class(instance=queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkerACEViewSet(viewsets.ModelViewSet):
    queryset = WorkerAccessControlEntry.objects.all()
    serializer_class = WorkerACESerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        existing = request.user.access_groups.filter(id=data.get('group', -1)).first()
        if not existing:
            return Response(data={"message": "Invalid group id"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            instance = serializer.create()
            return Response(data=self.serializer_class(instance=instance).data, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['get'], url_path='list-by-group')
    def list_by_group(self, request, *args, **kwargs):
        group = request.query_params.get('group', -1)

        entries = self.queryset.filter(group_id=group, group__requester=request.user)
        serializer = self.serializer_class(instance=entries, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        update_worker_cache([instance.worker_id], constants.ACTION_GROUP_REMOVE, value=instance.group_id)
        instance.delete()
        return Response(data={"pk": pk}, status=status.HTTP_200_OK)


class RequesterACGViewSet(viewsets.ModelViewSet):
    queryset = RequesterAccessControlGroup.objects.all()
    serializer_class = RequesterACGSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        is_global = data.get('is_global', True)
        type = data.get('type', RequesterAccessControlGroup.TYPE_DENY)
        existing_group = request.user.access_groups.filter(type=type,
                                                           is_global=is_global).first()
        if existing_group and is_global:
            return Response(data={"message": "Already exists"}, status=status.HTTP_200_OK)

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            instance = serializer.create(requester=request.user)
            return Response(data=self.serializer_class(instance=instance).data, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['get'], url_path='retrieve-global')
    def retrieve_global(self, request, *args, **kwargs):
        entry_type = request.query_params.get('type', RequesterAccessControlGroup.TYPE_DENY)
        group = self.queryset.filter(is_global=True, type=entry_type,
                                     requester=request.user).first()
        serializer = self.serializer_class(instance=group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['post'], url_path='create-with-entries')
    def create_with_members(self, request, *args, **kwargs):
        entries = request.data.pop('entries')
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            entry = None
            with transaction.atomic():
                entry = serializer.create_with_entries(requester=request.user, entries=entries)
            return Response(data={
                'id': entry.id,
                'name': entry.name
            }, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['get'], url_path='list-favorites')
    def list_favorites(self, request, *args, **kwargs):
        groups = self.queryset.filter(requester=request.user, is_global=False,
                                      type=RequesterAccessControlGroup.TYPE_ALLOW)
        serializer = self.serializer_class(instance=groups, many=True, fields=('id', 'name'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)
