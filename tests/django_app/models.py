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
    INSTALLED_APPS=('django.contrib.contenttypes', 'django.contrib.auth', 'tests.django_app',)
)

from django.db import models


class Rabbit(models.Model):
    title = models.CharField(max_length=16)
    username = models.CharField(max_length=16)
    active = models.BooleanField()
    email = models.EmailField()
    description = models.TextField()

    created_at = models.DateField()
    updated_at = models.DateTimeField()

    opened_at = models.TimeField()
    percent = models.FloatField()
    money = models.IntegerField()
    ip = models.IPAddressField()

    some_field = models.CommaSeparatedIntegerField(max_length=12)
    funny = models.NullBooleanField(null=False, blank=False)
    slug = models.SlugField()
    speed = models.DecimalField(max_digits=3, decimal_places=1)


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
