from rest_framework import viewsets, status
from rest_framework.response import Response

from crowdsourcing.serializers.template import *


class TemplateViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Template

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer


class TemplateItemViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TemplateItem

    queryset = TemplateItem.objects.all()
    serializer_class = TemplateItemSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        item_serializer = TemplateItemSerializer(instance=instance, data=request.data, partial=True)
        if item_serializer.is_valid():
            item_serializer.update(instance=instance, validated_data=item_serializer.validated_data)
            return Response(data={"message": "Item updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(data=item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TemplateItemPropertiesViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TemplateItemProperties

    queryset = TemplateItemProperties.objects.all()
    serializer_class = TemplateItemPropertiesSerializer
