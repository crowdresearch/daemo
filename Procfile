web: gunicorn csp.wsgi --log-file -
worker: celery -A csp worker -B -q
