import StringIO
import zipfile
from collections import OrderedDict
from django.http import HttpResponse
from django.db.models import Q
import pandas as pd
from rest_framework import status, mixins, serializers
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from crowdsourcing.models import BatchFile, TaskWorker, TaskWorkerResult, Project
from crowdsourcing.serializers.file import BatchFileSerializer


class FileViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = BatchFile.objects.filter(deleted_at__isnull=True)
    serializer_class = BatchFileSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = BatchFileSerializer(data=request.data)
        if serializer.is_valid():
            batch_file = serializer.create()
            serializer = BatchFileSerializer(instance=batch_file)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    @list_route(methods=['get'], url_path='download-results')
    def download_results(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id', -1)
        project = Project.objects.filter(id=project_id, owner=request.user).first()
        if project is None:
            return Response([], status=status.HTTP_404_NOT_FOUND)

        revisions = Project.objects.prefetch_related('template', 'template__items', 'batch_files').filter(
            ~Q(status=Project.STATUS_DRAFT), group_id=project.group_id).order_by('-id')

        if len(revisions) == 1 and revisions[0].template.items.filter(type='file_upload').count() == 0:
            data, rows = self._fetch_results(revisions[0].id, revisions[0].batch_files.first())
            # http_status = status.HTTP_200_OK if rows > 0 else status.HTTP_204_NO_CONTENT
            resp = HttpResponse(data)
            resp['Content-Disposition'] = 'attachment; filename={}.csv'.format(revisions[0].name.replace(' ', '_'))
            resp['Content-Type'] = 'text/csv'
            return resp
            # return Response(data, http_status)
        else:
            zip_file_buffer = StringIO.StringIO()
            zip_file = zipfile.ZipFile(zip_file_buffer, "w")
            r = len(revisions)
            for rev in revisions:
                data, rows = self._fetch_results(rev.id, rev.batch_files.first())

                if rows > 0:
                    # file_upload_items = rev.template.items.filter(type='file_upload')
                    file_results = TaskWorkerResult.objects \
                        .prefetch_related('attachment').filter(attachment__isnull=False,
                                                               task_worker__status__in=[TaskWorker.STATUS_SUBMITTED,
                                                                                        TaskWorker.STATUS_ACCEPTED,
                                                                                        TaskWorker.STATUS_RETURNED],
                                                               task_worker__task__project_id=rev.id)
                    zip_file.writestr('{}/revision_{}({}).csv'.format(revisions[0].name.replace(' ', '_'), r, rev.id),
                                      data)
                    for f in file_results:
                        zip_file.writestr(
                            '{}/responses/{}_{}'.format(revisions[0].name.replace(' ', '_'), f.task_worker_id,
                                                        f.attachment.name),
                            f.attachment.file.read())
                r -= 1
            zip_file.close()
            resp = HttpResponse(zip_file_buffer.getvalue())
            resp['Content-Disposition'] = 'attachment; filename={}.zip'.format(revisions[0].name.replace(' ', '_'))
            resp['Content-Type'] = 'application/x-zip-compressed'
            return resp
            # return Response(data, status.HTTP_200_OK)

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

    def _fetch_results(self, project_id, attachment=None):
        task_worker_results = TaskWorkerResult.objects.select_related('task_worker__task', 'template_item',
                                                                      'task_worker__worker',
                                                                      'task_worker__worker__profile').filter(
            task_worker__task__project_id=project_id,
            task_worker__status__in=[TaskWorker.STATUS_ACCEPTED, TaskWorker.STATUS_REJECTED,
                                     TaskWorker.STATUS_SUBMITTED]).order_by(
            'task_worker__task_id',
            'task_worker__worker_id',
            'template_item__position')

        if task_worker_results.count() == 0:
            return [], 0

        task_worker_id = -1
        results = []
        for result in task_worker_results:
            if result.task_worker_id != task_worker_id:
                task_worker_id = result.task_worker_id
                results.append(OrderedDict([
                    ("id", result.task_worker_id),
                    ("task_id", result.task_worker.task_id),
                    ("created_at", result.task_worker.created_at),
                    ("submitted_timestamp", result.updated_at),
                    ("worker", result.task_worker.worker.profile.handle),
                    ("status", [x[1] for x in TaskWorker.STATUS if x[0] == result.task_worker.status][0])
                ]))
                task_data = result.task_worker.task.data
                if task_data:
                    if attachment is not None:
                        ordered_data = OrderedDict()
                        for ch in attachment.column_headers:
                            ordered_data[ch] = task_data[ch]
                        results[len(results) - 1].update(ordered_data)
                    else:
                        results[len(results) - 1].update(task_data)
            result_dict = self._to_dict(result)
            results[len(results) - 1].update(result_dict)
        df = pd.DataFrame(results)
        output = StringIO.StringIO()
        df.to_csv(output, columns=results[0].keys(), index=False, encoding="utf-8")
        data = output.getvalue()
        output.close()
        return data, task_worker_results.count()
