__author__ = 'dmorina'
from oauth2client import client
from oauth2_provider.oauth2_backends import OAuthLibCore, get_oauthlib_core
from oauthlib.common import urlencode, urlencoded, quote
#from oauth2_provider import
def oauth_create_client(user, client_name):
    #r_client = client.
    #r_client.save()
    #return r_client
    pass

class Oauth2Backend(OAuthLibCore):
    def _extract_params(self, request):
        """
        Extract parameters from the Django request object. Such parameters will then be passed to
        OAuthLib to build its own Request object. The body should be encoded using OAuthLib urlencoded
        """
        uri = self._get_escaped_full_path(request)
        http_method = request.method
        headers = {}#self.extract_headers(request)
        body = urlencode(self.extract_body(request))
        return uri, http_method, body, headers

    def create_token_response(self, request):
        """
        A wrapper method that calls create_token_response on `server_class` instance.
        :param request: The current django.http.HttpRequest object
        """
        uri, http_method, body, headers = self._extract_params(request)
        print(headers)
        headers, body, status = get_oauthlib_core().server.create_token_response(uri, http_method, body,
                                                                  headers)
        uri = headers.get("Location", None)

        return uri, headers, body, status

    def extract_body(self, request):
        """
        Extracts the POST body from the Django request object
        :param request: The current django.http.HttpRequest object
        :return: provided POST parameters
        """
        return request.data.items()


class Oauth2Login:

    def get_client_and_token(self,request, user):
        from oauth2_provider.models import Application
        oauth2_client = Application.objects.create(user=user,
                   client_type=Application.CLIENT_CONFIDENTIAL,
                   authorization_grant_type=Application.GRANT_PASSWORD)
        oauth2_backend = Oauth2Backend()
        uri, headers, body, status = oauth2_backend.create_token_response(request)
        response_data = {}
        response_data["client_id"]=oauth2_client.client_id
        response_data["client_secret"]=oauth2_client.client_secret
        response_data["grant_type"]="password"
        response_data["email"] = user.email
        response_data["username"] = user.username
        response_data["first_name"] = user.first_name
        response_data["last_name"] = user.last_name
        response_data["last_login"] = user.last_login
        response_data["date_joined"] = user.date_joined
        response_data["message"]="OK"
        return response_data, 200