from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from crowdsourcing.models import Task
from crowdsourcing.utils import get_delimiter
from django.http import HttpResponse
import pandas
import StringIO
from crowdsourcing.serializers.experimental import WorkerProjectsSerializer
from rest_framework.permissions import IsAuthenticated


class WorkerProjectsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, ]

    def get_projects(self, request, *args, **kwargs):
        worker_id = request.user.userprofile.worker.id
        query = '''
            SELECT  row_number() OVER () id, m.id module_id, p.id project_id, r.id requester_id, r.alias requester_name, p.name project_name,
                m.name module_name, m.description module_description, m.task_time "task_time_minutes", NULL AS rank
              FROM crowdsourcing_taskworker tw
              INNER JOIN crowdsourcing_task t ON t.id = tw.task_id
              INNER JOIN crowdsourcing_module m ON m.id=t.module_id
              INNER JOIN crowdsourcing_project p ON p.id = m.project_id
              INNER JOIN crowdsourcing_requester r ON r.id = m.owner_id
            WHERE tw.worker_id=%s AND tw.task_status IN (2,3,4,5)
            group by m.id, p.id, r.id, r.alias, p.name, m.name, m.description, m.task_time;
        '''
        data = Task.objects.raw(query, params=[worker_id])
        serializer = WorkerProjectsSerializer(data, many=True)
        column_headers = ['id', 'module_id', 'project_id', 'requester_id', 'requester_name', 'project_name',
                          'module_name', 'module_description', 'task_time_minutes', 'rank']
        df = pandas.DataFrame(serializer.data)
        df = df[column_headers]
        output = StringIO.StringIO()
        df.to_csv(output, index=False, encoding="utf-8", sep=',')
        response_data = output.getvalue()
        output.close()
        response =  HttpResponse(response_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="task_ranking_'+str(worker_id)+'.csv"'
        return response