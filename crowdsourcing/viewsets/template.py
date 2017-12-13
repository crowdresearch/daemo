from django.db import transaction
from rest_framework import mixins
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.serializers.template import TemplateItemSerializer, TemplateItemPropertiesSerializer, \
    TemplateSerializer


class TemplateViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    from crowdsourcing.models import Template

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.create(with_defaults=False, owner=request.user, is_review=False)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id": instance.id})

    def list(self, request, *args, **kwargs):
        return Response(self.serializer_class(instance=request.user.templates.all().order_by('-id'), many=True).data)

    @detail_route(methods=['get'])
    def items(self, request, *args, **kwargs):
        instance = self.queryset.filter(owner=request.user, id=kwargs.get('pk')).first()
        if instance is None:
            return Response({"message": "Template not found!"}, status=status.HTTP_404_NOT_FOUND)
        return Response(TemplateItemSerializer(instance=instance.items.all(), many=True).data)


class TemplateItemViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TemplateItem

    queryset = TemplateItem.objects.all()
    serializer_class = TemplateItemSerializer

    def list(self, request, *args, **kwargs):
        template_id = request.query_params.get('template_id')
        items = self.queryset.filter(template_id=template_id, template__owner=request.user)
        response = {
            "count": len(self.serializer_class(instance=items, many=True).data),
            "next": None,
            "previous": None,
            "results": self.serializer_class(instance=items, many=True).data
        }
        return Response(response)

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
        item = self.queryset.filter(template__owner=request.user, id=kwargs.get('pk')).first()
        if item is None:
            return Response({"message": "Item not found!"}, status.HTTP_404_NOT_FOUND)
        if item.successors.all().count() > 0:
            item.successors.all().update(predecessor=item.predecessor)

        item.delete()
        return Response({})


class TemplateItemPropertiesViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TemplateItemProperties

    queryset = TemplateItemProperties.objects.all()
    serializer_class = TemplateItemPropertiesSerializer
