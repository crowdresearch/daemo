__author__ = 'dmorina'
from csp import settings
import httplib2
from django.http import HttpResponse, HttpResponseRedirect
from crowdsourcing import models
from rest_framework.views import APIView

class GoogleDriveOauth(APIView):

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
        return HttpResponseRedirect(authorize_url)

    def auth_end(self, request):
        from oauth2client.django_orm import Storage
        from apiclient.discovery import build
        auth_flow = models.FlowModel.objects.get(id=request.user).flow
        credentials = auth_flow.step2_exchange(request.GET.get('code'))
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
                temporary_flow = models.TemporaryFlowModel.objects.get(email=user_info['emailAddress'], type='GOOGLEDRIVE', user= request.user)
                try:
                    account_check = models.AccountModel.objects.get(type='GOOGLEDRIVE', email=user_info['emailAddress'])
                    account_check.is_active = 1
                    account_check.status = 1
                    account_check.save()
                    message = 'Account already linked. We have re-activated it for you.'
                except models.AccountModel.DoesNotExist:
                    account = models.AccountModel()
                    account.owner = request.user
                    account.email = user_info['emailAddress']
                    account.access_token = credentials.to_json()
                    account.description = user_info['displayName'] + '(' + user_info['emailAddress']+')'
                    account.type = 'GOOGLEDRIVE'
                    account.quota = quota_bytes_total
                    account.assigned_space = quota_bytes_total
                    account.used_space = drive_bytes_used
                    account.is_active = 1
                    body = {
                        'title': 'Uberbox',
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                    account.root = drive_service.files().insert(body=body).execute()['id']
                    account.name = 'Google Drive'
                    account.status = 1
                    account.save()
                    storage = Storage(models.CredentialsModel, 'account', account, 'credential')
                    storage.put(credentials)
                    credentials.to_json()
                temporary_flow.delete()
            except models.TemporaryFlowModel.DoesNotExist:
                message= 'The provided email does not match with the actual Google email.'
        except Exception as e:
            message = 'Something went wrong.'

        return HttpResponseRedirect('/')