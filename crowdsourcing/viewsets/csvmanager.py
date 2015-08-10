from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from crowdsourcing.serializers.requesterinputfile import RequesterInputFileSerializer
from crowdsourcing.serializers.task import TaskSerializer
from crowdsourcing.models import RequesterInputFile, Task
import pandas as pd
import csv
import StringIO

class CSVManagerViewSet(ViewSet):
	queryset = RequesterInputFile.objects.filter(deleted=False)
	serializer_class = RequesterInputFileSerializer

	def get_metadata_and_save(self, request, *args, **kwargs):
		uploadedFile = request.data['file']
		csvinput = csv.reader(uploadedFile)
		column_headers = csvinput.next()
		num_rows = sum(1 for row in csvinput)
		serializer = RequesterInputFileSerializer(data=request.data)
		if serializer.is_valid():
			id = serializer.create()
			metadata = {'id': id, 'num_rows': num_rows, 'column_headers': column_headers}
			return Response({'metadata': metadata})
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	def get_results_file(self, request, *args, **kwargs):
		module_name = request.query_params.get('moduleName')
		project_name = request.query_params.get('projectName')
		module = request.query_params.get('id')
		task = Task.objects.filter(module=module)
		task_serializer = TaskSerializer(task, many=True)
		tasks = task_serializer.data
		column_headers = ['created', 'last_updated', 'status', 'worker']
		data_keys = eval(tasks[0]['data']).keys()
		for key in data_keys:
			column_headers.append(key)
		for i in xrange(1, len(data_keys) + 1):
			column_headers.append('Output_' + str(i))
		data = []
		entries = []
		for task in tasks:
			task_workers = task['task_workers']
			for task_worker in task_workers:
				task_worker_results = task_worker['task_worker_results']
				results = []
				for task_worker_result in task_worker_results:
					results.append(task_worker_result['result'])
				entry = {'id': task_worker['id'], 'data': task['data'], 'worker_alias': task_worker['worker_alias'],
						'status': task_worker['status'], 'results': results, 'created': task_worker['created_timestamp'],
						'last_updated': task_worker['last_updated']}
				entries.append(entry)
		for entry in entries:
			temp = [entry['created'], entry['last_updated'], entry['status'], entry['worker_alias']]
			for key in data_keys:
				temp.append(eval(entry['data'])[key])
			for result in entry['results']:
				temp.append(result)
			data.append(temp)
		df = pd.DataFrame(data)
		output = StringIO.StringIO()
		df.to_csv(output, header=column_headers, index=False)
		return Response(output.getvalue())

