from __future__ import absolute_import

from django.conf import settings

settings.configure(
    ROOT_URLCONF='tests.django_app.urls',
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'USER': '',
            'PASSWORD': '',
            'TEST_CHARSET': 'utf8',
        }
    },
    INSTALLED_APPS=('tests.django_app',)
)
