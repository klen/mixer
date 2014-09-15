import tempfile

TMPDIR = tempfile.mkdtemp()

ROOT_URLCONF = 'tests.django_app.urls'

SECRET_KEY = 'KeepMeSecret'

DEBUG = True

MEDIA_ROOT = TMPDIR

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware')

INSTALLED_APPS = 'django.contrib.contenttypes', 'django.contrib.auth', 'tests.django_app'
