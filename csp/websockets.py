"""
WSGI config for csp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from ws4redis.uwsgi_runserver import uWSGIWebsocketServer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csp.settings")

application = uWSGIWebsocketServer()
