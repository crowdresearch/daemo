from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from crowdsourcing.serializers.requester import *
from crowdsourcing.serializers.project import *


class RequesterViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Requester
    queryset = Requester.objects.all()
    serializer_class = RequesterSerializer

    @detail_route(methods=['GET'])
    def portfolio(self, request, *args, **kwargs):
        requester = self.get_object()
        projects = requester.project_set.all().filter(deleted=False, status=4)
        serializer = ProjectSerializer(instance=projects, many=True,
                                      fields=('id', 'name', 'icon', 'categories',
                                              'repetition', 'avg_rating', 'num_reviews', 'completed_on',
                                              'total_submissions', 'num_contributors',
                                              'num_raters', 'min_pay', 'avg_pay', 'num_accepted', 'num_rejected',
                                              'total_tasks'))
        return Response(serializer.data)


class QualificationViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Qualification
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer
