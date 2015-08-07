from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from crowdsourcing.serializers.requesterinputfile import RequesterInputFileSerializer
from crowdsourcing.serializers.task import TaskSerializer
from crowdsourcing.models import RequesterInputFile, Task
import csv

class RequesterInputFileViewSet(ViewSet):
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
		csv_data = []
		column_headers = ['created', 'last_updated', 'status', 'worker']
		data_keys = eval(tasks[0]['data']).keys()
		for key in data_keys:
			column_headers.append(key)
		for i in xrange(1, len(data_keys) + 1):
			column_headers.append('Output_' + str(i))
		data = [column_headers]
		for task in tasks:
			task_workers = task['task_workers']
			for task_worker in task_workers:
				task_worker_results = task_worker['task_worker_results']
				data_source_results = dict()
				for task_worker_result in task_worker_results:
					if task_worker_result['role'] != 'input': continue
					data_source_results[task_worker_result['data_source']] = task_worker_result['result']
				entry = dict()

		file_name = project_name.replace(" ", '') + module_name.replace(" ", '') + '.csv'
		with open(file_name, 'wb') as csvfile:
			filewriter = csv.writer(csvfile)
			filewriter.writerows(data)
		return Response(file_name)

