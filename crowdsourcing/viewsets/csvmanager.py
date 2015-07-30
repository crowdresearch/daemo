from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
import csv

class CSVManagerViewSet(ViewSet):

    def parse(self, request):
        uploadedFile = request.data['file']
        csvinput = csv.DictReader(uploadedFile)
        arr = []
        for row in csvinput:
            arr.append(row)
        return Response(arr)

    # def parse_backup(self, request):
    #     parent = request.data['parent']
    #     account = AccountModel.objects.get(owner=request.user, type='GOOGLEDRIVE')
    #     drive_util = GoogleDriveUtil(account_instance=account)
    #     file_list = drive_util.list_files_in_folder(parent, "blah")
    #     for fileobj in file_list:
    #         if '.csv' in fileobj['originalFilename']:
    #             file = fileobj
    #             break
    #     content = drive_util.download(file['id'])
    #     reader = csv.reader(content)
    #     formatted_file = []
    #     curr_arr = []
    #     curr_string = ""
    #     for row in reader:
    #         if row == ['', '']:
    #             curr_arr.append(curr_string)
    #             curr_string = ""
    #         if row == []:
    #             curr_arr.append(curr_string)
    #             formatted_file.append(curr_arr)
    #             curr_string = ""
    #             curr_arr = []
    #         else:
    #             curr_string += row[0]
    #     curr_arr.append(curr_string)
    #     formatted_file.append(curr_arr)
    #     return Response(formatted_file, 200)