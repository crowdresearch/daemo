from crowdsourcing.serializers.template import *
from rest_framework import viewsets


class TemplateViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Template

    queryset = Template.objects.all()
    serializer_class = TemplateSerializer


class TemplateItemViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TemplateItem

    queryset = TemplateItem.objects.all()
    serializer_class = TemplateItemSerializer


class TemplateItemPropertiesViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import TemplateItemProperties

    queryset = TemplateItemProperties.objects.all()
    serializer_class = TemplateItemPropertiesSerializer
