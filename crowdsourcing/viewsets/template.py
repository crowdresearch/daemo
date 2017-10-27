from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from django.db import transaction

from crowdsourcing.serializers.template import TemplateItemSerializer, TemplateItemPropertiesSerializer, \
    TemplateSerializer


class TemplateViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Template

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer


class TemplateItemViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TemplateItem

    queryset = TemplateItem.objects.all()
    serializer_class = TemplateItemSerializer

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.queryset.select_for_update().filter(id=kwargs.get('pk')).first()

            item_serializer = TemplateItemSerializer(instance=instance, data=request.data, partial=True)
            if item_serializer.is_valid():
                item_serializer.update(instance=instance, validated_data=item_serializer.validated_data)
            else:
                raise serializers.ValidationError(detail=item_serializer.errors)
        return Response(data={"message": "Item updated successfully"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        if item.successors.all().count() > 0:
            item.successors.all().update(predecessor=item.predecessor)

        item.delete()
        return Response({})


class TemplateItemPropertiesViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TemplateItemProperties

    queryset = TemplateItemProperties.objects.all()
    serializer_class = TemplateItemPropertiesSerializer
