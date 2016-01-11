import StringIO

from rest_framework.viewsets import GenericViewSet
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
import pandas as pd

from crowdsourcing.serializers.file import BatchFileSerializer
from crowdsourcing.serializers.task import TaskSerializer
from crowdsourcing.models import BatchFile, Task


class FileViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = BatchFile.objects.filter(deleted=False)
    serializer_class = BatchFileSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = BatchFileSerializer(data=request.data)
        if serializer.is_valid():
            batch_file = serializer.create()
            serializer = BatchFileSerializer(instance=batch_file)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'], url_path='download-results')
    def download_results(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id')
        task = Task.objects.filter(project=project_id)
        task_serializer = TaskSerializer(task, many=True, fields=('data', 'task_workers', 'comments'))
        tasks = task_serializer.data
        column_headers = ['task_status', 'worker_alias', 'created', 'last_updated', 'feedback']
        data_keys = tasks[0]['data'].keys()
        for key in data_keys:
            column_headers.append(key)
        data = []
        items = []
        for task in tasks:
            task_workers = task['task_workers']
            for task_worker in task_workers:
                task_worker_results = task_worker['task_worker_results']
                results = []
                for task_worker_result in task_worker_results:
                    results.append(task_worker_result['result'])
                item = {'id': task_worker['id'], 'data': task['data'], 'worker_alias': task_worker['worker_alias'],
                        'task_status': task_worker['task_status'], 'results': results,
                        'created': task_worker['created_timestamp'], 'last_updated': task_worker['last_updated'],
                        'feedback': ', '.join(map(lambda x: x['comment'].get('body', ''),
                                                  [comment for comment in task['comments']]))}
                items.append(item)
        max_results = 0
        for item in items:
            temp = [item['task_status'], item['worker_alias'], item['created'], item['last_updated'], item['feedback']]
            for key in data_keys:
                if key in item['data']:
                    temp.append(item['data'][key])
            num_results = 0
            for result in item['results']:
                num_results += 1
                temp.append(result)
            if num_results > max_results:
                max_results = num_results
            data.append(temp)
        for i in xrange(1, max_results + 1):
            column_headers.append('Output_' + str(i))
        df = pd.DataFrame(data)
        output = StringIO.StringIO()
        df.to_csv(output, header=column_headers, index=False, encoding="utf-8")
        data = output.getvalue()
        output.close()
        return Response(data, status.HTTP_200_OK)
