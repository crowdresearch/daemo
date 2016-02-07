DEBUG = True

COMPRESS_OFFLINE = False
COMPRESS_ENABLED = False

REGISTRATION_ALLOWED = True

CELERY_RESULT_BACKEND = 'redis://localhost:6379'
BROKER_URL = 'redis://localhost:6379'
CELERY_TIMEZONE = 'America/Los_Angeles'

SITE_HOST = 'https://localhost:8000'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "crowdsource_dev"
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
