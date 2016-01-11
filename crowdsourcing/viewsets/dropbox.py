from rest_framework.views import APIView
from django.http import HttpResponseRedirect

from csp import settings
from crowdsourcing import models


# TODO change this to support ajax requests, remove HttpResponseRedirect
class DropboxOauth(APIView):
    """
        Handles the Dropbox Oauth2 integration
    """

    def get_dropbox_auth_flow(self, request):
        from dropbox.client import DropboxOAuth2Flow
        redirect_uri = settings.DROPBOX_REDIRECT_URI
        auth_flow = DropboxOAuth2Flow(settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET, redirect_uri,
                                      request.session, "dropbox-auth-csrf-token")
        return auth_flow

    def dropbox_auth_start(self, request):
        auth_flow = self.get_dropbox_auth_flow(request)
        authorize_url = auth_flow.start()
        return HttpResponseRedirect(authorize_url)

    def dropbox_auth_finish(self, request):
        from dropbox.client import DropboxOAuth2Flow, DropboxClient
        access_token = None
        try:
            auth_flow = self.get_dropbox_auth_flow(request)
            access_token, user_id, url_state = auth_flow.finish(request.DATA)
        except DropboxOAuth2Flow.BadRequestException:
            # http_status(400)
            pass
        except DropboxOAuth2Flow.BadStateException:
            return HttpResponseRedirect("/api/dropbox/auth-start")
        except DropboxOAuth2Flow.CsrfException:
            # http_status(403)
            pass
        except DropboxOAuth2Flow.NotApprovedException:
            return HttpResponseRedirect("/")
        except DropboxOAuth2Flow.ProviderException:
            # http_status(403)
            pass
        client = DropboxClient(oauth2_access_token=access_token)
        try:
            account_info = client.account_info()
            temporary_flow = models.TemporaryFlowModel.objects.get(email=account_info['email'],
                                                                   type='DROPBOX', user=request.user)
            try:
                account_check = models.AccountModel.objects.get(type='DROPBOX', email=account_info['email'])
                account_check.is_active = 1
                account_check.status = 1
                account_check.save()
            except models.AccountModel.DoesNotExist:
                account = models.AccountModel()
                account.owner = request.user
                account.email = account_info['email']
                account.access_token = access_token
                account.description = account_info['display_name'] + '(' + account_info['email'] + ')'
                account.type = 'DROPBOX'
                account.quota = account_info['quota_info']['quota']
                account.used_space = account_info['quota_info']['normal']
                account.is_active = 1
                account.name = 'Dropbox'
                account.status = 1
                account.assigned_space = account_info['quota_info']['quota']
                account.save()
            temporary_flow.delete()
        except models.TemporaryFlowModel.DoesNotExist:
            pass

        return HttpResponseRedirect('/accounts')
