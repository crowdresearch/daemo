"""
WSGI config for csp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dj_static import Cling

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csp.settings")

application = get_wsgi_application()
_webserver = Cling(application)


def application(environ, start_response):
    from django.conf import settings

    if environ.get('PATH_INFO').startswith(settings.WEBSOCKET_URL):
        from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
        _websockets = uWSGIWebsocketServer()
        return _websockets(environ, start_response)
    return _webserver(environ, start_response)
