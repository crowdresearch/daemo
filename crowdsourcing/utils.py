__author__ = 'dmorina'
from oauth2_provider.oauth2_backends import OAuthLibCore, get_oauthlib_core
from django.utils.http import urlencode
import ast

def get_model_or_none(model, *args, **kwargs):
    """
        Get model object or return None, this will catch the DoesNotExist error.

        Keyword Arguments:
        model -- this is the model you want to query from
        other parameters are of variable length: e.g id=1 or username='jon.snow'

    """
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None

class Oauth2Backend(OAuthLibCore):
    def _extract_params(self, request):
        """
        Extract parameters from the Django request object. Such parameters will then be passed to
        OAuthLib to build its own Request object. The body should be encoded using OAuthLib urlencoded
        """
        uri = self._get_escaped_full_path(request)
        http_method = request.method
        headers = {}#self.extract_headers(request)
        body = urlencode(self.extract_body(request)) #TODO
        return uri, http_method, body, headers

    def create_token_response(self, request):
        """
        A wrapper method that calls create_token_response on `server_class` instance.
        :param request: The current django.http.HttpRequest object
        """
        uri, http_method, body, headers = self._extract_params(request)
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


class Oauth2Utils:

    def create_client(self, request, user):
        from oauth2_provider.models import Application
        oauth2_client = Application.objects.create(user=user,
                   client_type=Application.CLIENT_CONFIDENTIAL,
                   authorization_grant_type=Application.GRANT_PASSWORD)
        return oauth2_client

    def get_token(self,request):
        oauth2_backend = Oauth2Backend()
        uri, headers, body, status = oauth2_backend.create_token_response(request)

        response_data = {}
        response_data["message"]="OK"
        response_data.update(ast.literal_eval(body))
        return response_data, 200

    def get_refresh_token(self, request):
        pass