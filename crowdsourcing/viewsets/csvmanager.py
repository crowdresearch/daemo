from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from crowdsourcing.serializers.requesterinputfile import RequesterInputFileSerializer
from crowdsourcing.serializers.task import TaskSerializer
from crowdsourcing.models import RequesterInputFile, Task
from crowdsourcing.utils import get_delimiter
import pandas as pd
import StringIO


class CSVManagerViewSet(ViewSet):
    queryset = RequesterInputFile.objects.filter(deleted=False)
    serializer_class = RequesterInputFileSerializer

    def get_metadata_and_save(self, request, *args, **kwargs):
        uploadedFile = request.data['file']
        delimiter = get_delimiter(uploadedFile.name)
        df = pd.DataFrame(pd.read_csv(uploadedFile, sep=delimiter))
        column_headers = list(df.columns.values)
        num_rows = len(df.index)
        serializer = RequesterInputFileSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.create()
            first_row = dict(zip(column_headers, list(df.values[0])))
            metadata = {'id': id, 'num_rows': num_rows, 'column_headers': column_headers, 'first': first_row}
            return Response({'metadata': metadata})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def download_results(self, request, *args, **kwargs):
        module_id = request.query_params.get('module_id')
        task = Task.objects.filter(module=module_id)
        task_serializer = TaskSerializer(task, many=True, fields=('data', 'task_workers', 'comments'))
        tasks = task_serializer.data
        column_headers = ['task_status', 'worker_alias', 'created', 'last_updated', 'feedback']
        data_keys = eval(tasks[0]['data']).keys()
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
                        'feedback': ', '.join(map(lambda x: x['comment'].get('body',''), [comment for comment in task['comments']])) }
                items.append(item)
        max_results = 0
        for item in items:
            temp = [item['task_status'], item['worker_alias'], item['created'], item['last_updated'], item['feedback']]
            for key in data_keys:
                temp.append(eval(item['data'])[key])
            num_results = 0
            for result in item['results']:
                num_results += 1
                temp.append(result)
            if num_results > max_results: max_results = num_results
            data.append(temp)
        for i in xrange(1, max_results + 1):
            column_headers.append('Output_' + str(i))
        df = pd.DataFrame(data)
        output = StringIO.StringIO()
        df.to_csv(output, header=column_headers, index=False, encoding="utf-8")
        data = output.getvalue()
        output.close()
        return Response(data, status.HTTP_200_OK)
