{%- from "ck/map.jinja" import crypt_keeper with context %}
import os
import logging.config
from .configuration import Configuration

ALLOWED_HOSTS = [
    '{{ crypt_keeper.url }}',
    'localhost',
]
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)
BASE_INSTALL_DIR = '{{ crypt_keeper.base_dir }}'
BASE_DIR = os.path.join(BASE_INSTALL_DIR, 'crypt-keeper/crypt-keeper-django/crypt_keeper_server')
CONFIGURATION_FILE_NAME = os.path.join(BASE_INSTALL_DIR, 'crypt_keeper_config.yml')
DATABASES = {
    'default': {
        'TEST': {
            'NAME': None,
            'COLLATION': None,
            'CHARSET': None,
            'MIRROR': None,
        },
        'AUTOCOMMIT': True,
        'TIME_ZONE': None,
        'CONN_MAX_AGE': 0,
        'USER': 'ck',
        'PASSWORD': 'Passw0rd',
        'PORT': '',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ck',
        'ATOMIC_REQUESTS': False,
        'HOST': 'localhost',
        'OPTIONS': {},
    },
}
DEBUG = True
INSTALLED_APPS = (
    'document_service',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'document_description_store',
    'secret_store',
    'tastypie',
    'guardian',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)
PROJECT_NAME = 'Crypt-Keeper'
ROOT_URLCONF = 'crypt_keeper_server.urls'
SECRET_KEY = '67f+0t&i-0j3*hicao!9tn)jk!rm8)5)mz*zsypximc7rn$4)-'
SETTINGS_MODULE = 'crypt_keeper_server.settings'
STATICFILES_DIRS = (
    os.path.join(
        BASE_DIR,
        'crypt_keeper_server/static',
    ),
)
STATIC_ROOT = os.path.join(BASE_INSTALL_DIR, 'static')
STATIC_URL = '/static/'
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ]
        },
        'APP_DIRS': True,
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': []
    }
]
TIME_ZONE = 'UTC'
USE_L10N = True
USE_TZ = True
WSGI_APPLICATION = 'crypt_keeper_server.wsgi.application'

# Configure logging

CONFIGURATION = Configuration(CONFIGURATION_FILE_NAME)
LOG_FORMAT = CONFIGURATION.lookup('log:format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT,
        },
        'simple': {
            'format': '%(levelname)s [%(name)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'ck-file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '{{ crypt_keeper.log_dir }}/{{ crypt_keeper.log_name }}',
            'formatter': 'verbose',
        },
        'django-file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '{{ crypt_keeper.log_dir }}/{{ crypt_keeper.django_log_name }}',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django-file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'crypt-keeper': {
            'handlers': ['ck-file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },

    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
}
