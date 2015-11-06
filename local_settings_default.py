DEBUG = True
COMPRESS_OFFLINE = False
COMPRESS_ENABLED = False
REGISTRATION_ALLOWED = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "crowdsource_dev"
    }
}