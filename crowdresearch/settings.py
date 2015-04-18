"""
Django settings for crowdsourcing project.

For more information on this file, see

For the full list of settings and their values, see
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7rtj$)63_8qp3=!32fx-zub$pm5k^adtg*ywx=jkce!be3)1b3'

# SECURITY WARNING: don't run with debug turned on in production! @
DEBUG = True

TEMPLATE_DEBUG = True
APPEND_SLASH = True
#ALLOWED_HOSTS = ['localhost','127.0.0.1','google.com']
ALLOWED_HOSTS = []


#Will be used in the future for Mobile devices and other desktop clients, APIs
REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
         'rest_framework.authentication.SessionAuthentication',),
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'rest_framework',
    'crowdsourcing',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'crowdresearch.urls'

WSGI_APPLICATION = 'crowdresearch.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'crowdresearch.db',
    }
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'staticfiles'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)
COMPRESS_ROOT = '/compress'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)

# Email
EMAIL_HOST = 'localhost'
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True

# Others
REGISTRATION_ALLOWED = True
PASSWORD_RESET_ALLOWED = True
EMAIL_ENABLED = False
EMAIL_SENDER = 'drm.mrn@gmail.com'
LOGIN_URL = '/login'
#SESSION_ENGINE = 'redis_sessions.session'

# Security
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
