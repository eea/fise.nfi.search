# Settings module for running tests
# Use:  ./manage.py test --settings=nfi_search.settings.test

from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': env('ELASTICSEARCH_TEST_HOST'),
        'http_auth': env('ELASTICSEARCH_TEST_AUTH'),
    },
}

SECRET_KEY = 'secret'
