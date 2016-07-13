from django.core.exceptions import PermissionDenied
from oauth2_provider.oauth2_backends import get_oauthlib_core
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user

try:
    # django >= 1.8 && python >= 2.7
    # https://docs.djangoproject.com/en/1.8/releases/1.7/#django-utils-dictconfig-django-utils-importlib
    from importlib import import_module
except ImportError:
    # RemovedInDjango19Warning: django.utils.importlib will be removed in Django 1.9.
    from django.utils.importlib import import_module


def ws4redis_process_request(request):
    if request.META['PATH_INFO'] in settings.WS_API_URLS:
        request.session = None
        user, token = authenticate(request=request)
        if user is None:
            raise PermissionDenied
        request.user = user
    else:
        process_request(request)


def authenticate(request):
    """
    Returns two-tuple of (user, token) if authentication succeeds,
    or None otherwise.
    """
    oauthlib_core = get_oauthlib_core()
    valid, r = oauthlib_core.verify_request(request, scopes=[])
    if valid:
        return r.user, r.access_token
    else:
        return None, None


def process_request(request):
    request.session = None
    request.user = None
    session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
    if session_key is not None:
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore(session_key)
        request.user = SimpleLazyObject(lambda: get_user(request))
