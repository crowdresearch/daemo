import StringIO
from collections import OrderedDict
from rest_framework.viewsets import GenericViewSet
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
import pandas as pd

from crowdsourcing.serializers.file import BatchFileSerializer
from crowdsourcing.models import BatchFile, Task, TaskWorker, TaskWorkerResult


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
        project_id = request.query_params.get('project_id', -1)

        task_worker_results = TaskWorkerResult.objects.select_related('task_worker__task', 'template_item',
                                                                      'task_worker__worker').filter(
            task_worker__task__project_id=project_id,
            task_worker__task_status__in=[TaskWorker.STATUS_ACCEPTED, TaskWorker.STATUS_REJECTED,
                                          TaskWorker.STATUS_SUBMITTED]).order_by(
            'task_worker__task_id',
            'task_worker__worker_id',
            'template_item__position')

        if task_worker_results.count() == 0:
            return Response(data=[], status=status.HTTP_204_NO_CONTENT)

        task_worker_id = -1
        results = []
        for result in task_worker_results:
            if result.task_worker_id != task_worker_id:
                task_worker_id = result.task_worker_id
                results.append(OrderedDict([
                    ("id", result.task_worker_id),
                    ("task_id", result.task_worker.task_id),
                    ("created_timestamp", result.task_worker.created_timestamp),
                    ("submitted_timestamp", result.last_updated),
                    ("worker_alias", result.task_worker.worker.alias),
                    ("status", [x[1] for x in TaskWorker.STATUS if x[0] == result.task_worker.task_status][0])
                ]))
                task_data = result.task_worker.task.data
                if task_data:
                    results[len(results) - 1].update(task_data)
            result_dict = self._to_dict(result)
            results[len(results) - 1].update(result_dict)

            # task = Task.objects.filter(project=project_id)
            # task_serializer = TaskSerializer(task, many=True, fields=('data', 'task_workers'))
            # tasks = task_serializer.data
            # column_headers = ['task_status', 'worker_alias', 'created', 'last_updated']
            # data_keys = tasks[0]['data'].keys()
            # for key in data_keys:
            #     column_headers.append(key)
            # data = []
            # items = []
            # for task in tasks:
            #     task_workers = task['task_workers']
            #     for task_worker in task_workers:
            #         task_worker_results = task_worker['task_worker_results']
            #         results = []
            #         for task_worker_result in task_worker_results:
            #             results.append(task_worker_result['result'])
            #         item = {'id': task_worker['id'], 'data': task['data'], 'worker_alias': task_worker['worker_alias'],
            #                 'task_status': task_worker['task_status'], 'results': results,
            #                 'created': task_worker['created_timestamp'], 'last_updated': task_worker['last_updated']}
            #         items.append(item)
            # max_results = 0
            # for item in items:
            #     temp = [item['task_status'], item['worker_alias'], item['created'], item['last_updated']]
            #     for key in data_keys:
            #         if key in item['data']:
            #             temp.append(item['data'][key])
            #     num_results = 0
            #     for result in item['results']:
            #         num_results += 1
            #         temp.append(result)
            #     if num_results > max_results:
            #         max_results = num_results
            #     data.append(temp)
            # for i in xrange(1, max_results + 1):
            #     column_headers.append('Output_' + str(i))
            df = pd.DataFrame(results)
            output = StringIO.StringIO()
            df.to_csv(output, columns=results[0].keys(), index=False, encoding="utf-8")
            data = output.getvalue()
            output.close()
            return Response(data, status.HTTP_200_OK)

    @staticmethod
    def _to_dict(result):
        if result.template_item.type == 'checkbox':
            return {
                str(result.template_item.aux_attributes['question']['value']): ",".join(
                    [x['value'] for x in result.result if
                     'answer' in x and x['answer']])
            }
        elif result.template_item.type == 'iframe' and isinstance(result.result, list):
            return {
                "result": result.result
            }
        elif result.template_item.type == 'iframe' and isinstance(result.result, dict):
            return result.result
        else:
            return {
                str(result.template_item.aux_attributes['question']['value']): result.result
            }
