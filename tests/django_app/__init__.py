import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.django_app.settings')

from django import VERSION

if VERSION >= (1, 7):
    from django.apps import apps
    from django.conf import settings

    apps.populate(settings.INSTALLED_APPS)
