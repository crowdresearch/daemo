__author__ = 'dmorina'
from csp import settings

def get_google_auth_flow(request):
    from oauth2client.client import OAuth2WebServerFlow
    auth_flow = OAuth2WebServerFlow(settings.GOOGLE_DRIVE_CLIENT_ID, settings.GOOGLE_DRIVE_CLIENT_SECRET, settings.GOOGLE_DRIVE_OAUTH_SCOPE, settings.GOOGLE_DRIVE_REDIRECT_URI, approval_prompt='force', access_type='offline')
    return auth_flow