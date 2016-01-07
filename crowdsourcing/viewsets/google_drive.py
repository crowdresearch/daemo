import httplib2
from apiclient import discovery, errors
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from csp import settings
from crowdsourcing import models
from apiclient.http import MediaFileUpload
from crowdsourcing.models import AccountModel


# TODO add support for api ajax calls
class GoogleDriveOauth(ViewSet):
    permission_classes = [IsAuthenticated]

    def get_flow(self, request):
        from oauth2client.client import OAuth2WebServerFlow
        auth_flow = OAuth2WebServerFlow(settings.GOOGLE_DRIVE_CLIENT_ID, settings.GOOGLE_DRIVE_CLIENT_SECRET,
                                        settings.GOOGLE_DRIVE_OAUTH_SCOPE, settings.GOOGLE_DRIVE_REDIRECT_URI,
                                        approval_prompt='force', access_type='offline')
        return auth_flow

    def auth_init(self, request):
        auth_flow = self.get_flow(request)
        flow_model = models.FlowModel()
        flow_model.flow = auth_flow
        flow_model.id = request.user
        flow_model.save()
        authorize_url = auth_flow.step1_get_authorize_url()
        return Response({'authorize_url': authorize_url}, status=status.HTTP_200_OK)

    def auth_end(self, request):
        from oauth2client.django_orm import Storage
        from apiclient.discovery import build
        auth_flow = models.FlowModel.objects.get(id=request.user).flow
        credentials = auth_flow.step2_exchange(request.data.get('code'))
        http = httplib2.Http()
        http = credentials.authorize(http)

        drive_service = build('drive', 'v2', http=http)
        try:
            account_info = drive_service.about().get().execute()
            user_info = account_info['user']
            quota_info = account_info['quotaBytesByService']
            drive_quota = [drive['bytesUsed'] for drive in quota_info if drive['serviceName'] == 'DRIVE']
            drive_bytes_used = drive_quota.pop()
            quota_bytes_total = account_info['quotaBytesTotal']
            try:
                account_check = models.AccountModel.objects.get(type='GOOGLEDRIVE', email=user_info['emailAddress'])
                account_check.is_active = 1
                account_check.status = 1
                account_check.save()
            except models.AccountModel.DoesNotExist:
                account = models.AccountModel()
                account.owner = request.user
                account.email = user_info['emailAddress']
                account.access_token = credentials.to_json()
                account.description = user_info['displayName'] + '(' + user_info['emailAddress'] + ')'
                account.type = 'GOOGLEDRIVE'
                account.quota = quota_bytes_total
                account.assigned_space = quota_bytes_total
                account.used_space = drive_bytes_used
                account.is_active = 1
                body = {
                    'title': 'crowdresearch',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                account.root = drive_service.files().insert(body=body).execute()['id']
                account.name = 'Google Drive'
                account.status = 1
                account.save()
                storage = Storage(models.CredentialsModel, 'account', account, 'credential')
                storage.put(credentials)

        except Exception:
            Response({"message": "Failed to add account, please retry"}, status.HTTP_400_BAD_REQUEST)
        return Response({"message": "OK"}, status.HTTP_201_CREATED)


class GoogleDriveViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def query(self, request):
        file_name = request.query_params.get('path')
        files = file_name.split('/')
        account = AccountModel.objects.get(owner=request.user, type='GOOGLEDRIVE')
        root = account.root
        drive_util = GoogleDriveUtil(account_instance=account)
        file_list = []
        for file in files:
            file_list = drive_util.list_files_in_folder(root, "title = '" + file + "'")
            root = file_list[0]['id']
        return Response(file_list, 200)


class GoogleDriveUtil(object):
    def __init__(self, account_instance):
        credential_model = models.CredentialsModel.objects.get(account=account_instance)
        get_credential = credential_model.credential
        http = httplib2.Http()
        http = get_credential.authorize(http)
        drive_service = discovery.build('drive', 'v2', http=http)
        self.drive_service = drive_service

    def list_files_in_folder(self, folder_id, q):
        # TODO filter by q
        file_list = []
        page_token = None
        while True:
            try:
                params = {}
                if page_token:
                    params['pageToken'] = page_token
                    params['q'] = q
                children = self.drive_service.children().list(folderId=folder_id, **params).execute()
                for child in children.get('items', []):
                    file_list.append(self.drive_service.files().get(fileId=child['id']).execute())
                page_token = children.get('nextPageToken')
                if not page_token:
                    break
            except errors.HttpError as error:
                message = 'An error occurred: ' + error.content
                return message
        return file_list

    def search_file(self, account_instance, file_title):
        root_id = models.CredentialsModel.objects.get(account=account_instance).account.root
        parent_id = self.getPathId(root_id)  # get the id of the parent folder
        query = str(parent_id) + ' in parents and title=' + file_title
        contents = self.list_files_in_folder(parent_id, query)
        return contents

    def create_folder(self, title, parent_id='', mime_type='application/vnd.google-apps.folder'):
        body = {
            'title': title,
            'mimeType': mime_type
        }
        if parent_id:
            body['parents'] = [{'id': parent_id}]
        try:
            file = self.drive_service.files().insert(body=body).execute()
            return file
        except errors.HttpError:
            return None

    def insert(self, file_name, title, parent_id=[], mime_type='application/octet-stream', resumable=True):
        media_body = MediaFileUpload(file_name, mimetype=mime_type, resumable=resumable)
        body = {
            'title': title,
            'mimeType': mime_type
        }
        if parent_id:
            body['parents'] = [{'id': parent_id}]

        try:
            file = self.drive_service.files().insert(body=body, media_body=media_body).execute()
            return file
        except errors.HttpError:
            return None

    def update(self, file_id, new_revision, new_filename, mime_type='application/octet-stream'):
        try:
            # First retrieve the file from the API.
            file = self.drive_service.files().get(fileId=file_id).execute()

            # File's new content.
            media_body = MediaFileUpload(new_filename, mimetype=mime_type, resumable=True)

            # Send the request to the API.
            updated_file = self.drive_service.files().update(
                fileId=file_id,
                body=file,
                newRevision=new_revision,
                media_body=media_body).execute()
            return updated_file
        except errors.HttpError:
            return None

    def trash(self, file_id):
        try:
            return self.drive_service.files().trash(fileId=file_id).execute()
        except errors.HttpError as error:
            return str(error)

    def untrash(self, file_id):
        try:
            return self.drive_service.files().untrash(fileId=file_id).execute()
        except errors.HttpError:
            return None

    def delete(self, file_id):
        try:
            return self.drive_service.files().delete(fileId=file_id).execute()
        except errors.HttpError:
            return None

    def download(self, file_id):
        file = None
        try:
            file = self.drive_service.files().get(fileId=file_id).execute()
        except errors.HttpError:
            return None
        download_url = file.get('downloadUrl')
        if download_url:
            resp, content = self.drive_service._http.request(download_url)
            if resp.status == 200:
                return content
            else:
                return None
        else:
            return None

    def get(self, file_id):
        try:
            file = self.drive_service.files().get(fileId=file_id).execute()
            return file
        except errors.HttpError:
            return None

    def get_account_info(self):
        account_info = self.drive_service.about().get().execute()
        return account_info
