from crowdsourcing.serializers.requester import *
from crowdsourcing.serializers.project import *
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from crowdsourcing.models import Module
class RequesterViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Requester
    queryset = Requester.objects.all()
    serializer_class = RequesterSerializer
    @detail_route(methods = ['GET'])
    def portfolio(self, request, *args, **kwargs):
        requester = self.get_object()
        modules = requester.module_set.all().filter(deleted=False,status=4)
        serializer = ModuleSerializer(instance = modules,many = True,fields = ('id', 'name', 'icon', 'project', 'categories',
                  'repetition','avg_rating','num_reviews','completed_on','total_submissions','num_contributors',
                  'num_raters','min_pay','avg_pay','num_accepted','num_rejected','total_tasks'))
        return Response(serializer.data)


class RequesterRankingViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import RequesterRanking
    queryset = RequesterRanking.objects.all()
    serializer_class = RequesterRankingSerializer


class QualificationViewSet(viewsets.ModelViewSet):
    from crowdsourcing.models import Qualification
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer