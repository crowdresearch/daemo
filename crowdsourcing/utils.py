#from oauth2_provider import
__author__ = 'dmorina'
from oauth2_provider.oauth2_backends import OAuthLibCore, get_oauthlib_core
from oauth2client import client
from oauthlib.common import urlencode, urlencoded, quote
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
        print("extract body")
        print(request.data)
        return request.data.items()