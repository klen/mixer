from django.conf import settings
import tempfile

TMPDIR = tempfile.mkdtemp()

settings.configure(
    ROOT_URLCONF='tests.django_app.urls',
    DEBUG=True,
    MEDIA_ROOT=TMPDIR,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'USER': '',
            'PASSWORD': '',
            'TEST_CHARSET': 'utf8',
        }
    },
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'tests.django_app',)
)

from django.db import models
from django.contrib.auth.models import User


class Customer(User):
    name = models.CharField(max_length=100)


class Rabbit(models.Model):
    title = models.CharField(max_length=16)
    username = models.CharField(max_length=16, unique=True)
    active = models.BooleanField()
    email = models.EmailField()
    description = models.TextField()

    created_at = models.DateField()
    updated_at = models.DateTimeField()

    opened_at = models.TimeField()
    percent = models.FloatField()
    money = models.IntegerField()
    ip = models.IPAddressField()
    picture = models.FileField(upload_to=TMPDIR)

    some_field = models.CommaSeparatedIntegerField(max_length=12)
    funny = models.NullBooleanField(null=False, blank=False)
    slug = models.SlugField()
    speed = models.DecimalField(max_digits=3, decimal_places=1)

    url = models.URLField(null=True, blank=True, default='')


class Hole(models.Model):
    title = models.CharField(max_length=16)
    size = models.SmallIntegerField()
    owner = models.ForeignKey(Rabbit)
    # wtf = models.ForeignKey('self')


class Hat(models.Model):
    color = models.CharField(max_length=50, choices=(
        ('RD', 'red'),
        ('GRN', 'green'),
        ('BL', 'blue'),
    ))
    brend = models.CharField(max_length=10, default='wood')
    owner = models.ForeignKey(Rabbit, null=True, blank=True)


class Silk(models.Model):
    color = models.CharField(max_length=20)
    hat = models.ForeignKey(Hat)


class Door(models.Model):
    hole = models.ForeignKey(Hole)
    size = models.PositiveIntegerField()


class Number(models.Model):
    doors = models.ManyToManyField(Door)
    wtf = models.ManyToManyField('self')


class ColorNumber(Number):
    color = models.CharField(max_length=20)


class Client(models.Model):
    username = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=50)


class Message(models.Model):
    content = models.TextField()
    client = models.ForeignKey(Client)


class Tag(models.Model):
    title = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, blank=True, null=True)
    messages = models.ManyToManyField(Message, null=True, blank=True)
