from django.conf import settings
from django.contrib.contenttypes import models as ct_models

from django.db import models
from django.contrib.auth.models import User

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class CustomField(models.CharField):

    """ Custom field. """

    pass


class Customer(User):
    name = models.CharField(max_length=100)


class Rabbit(models.Model):
    title = models.CharField(max_length=16)
    username = models.CharField(max_length=16, unique=True)
    active = models.BooleanField(default=True)
    email = models.EmailField()
    text = models.TextField(max_length=512)

    created_at = models.DateField()
    updated_at = models.DateTimeField()

    opened_at = models.TimeField()
    percent = models.FloatField()
    money = models.IntegerField()
    ip = models.IPAddressField()
    ip6 = models.GenericIPAddressField(protocol='ipv6')
    picture = models.FileField(upload_to=settings.TMPDIR)

    some_field = models.CommaSeparatedIntegerField(max_length=12)
    funny = models.NullBooleanField(null=False, blank=False)
    slug = models.SlugField()
    speed = models.DecimalField(max_digits=3, decimal_places=1)

    url = models.URLField(null=True, blank=True, default='')

    file_path = models.FilePathField()
    content_type = models.ForeignKey(ct_models.ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    error_code = models.PositiveSmallIntegerField()
    custom = CustomField(max_length=24)
    content_object = GenericForeignKey('content_type', 'object_id')

    binary = models.BinaryField()

    one2one = models.OneToOneField('django_app.Simple', on_delete=models.CASCADE)

    def save(self, **kwargs):
        """ Custom save. """

        if not self.created_at:
            import datetime
            self.created_at = datetime.datetime.now()

        return super(Rabbit, self).save(**kwargs)


class Hole(models.Model):
    title = models.CharField(max_length=16)
    size = models.SmallIntegerField()
    owner = models.ForeignKey(Rabbit, on_delete=models.CASCADE)

    # FIXME compatibility
    rabbits = GenericRelation(Rabbit, **({'related_query_name': 'holes'}))


class Hat(models.Model):
    color = models.CharField(max_length=50, choices=(
        ('RD', 'red'),
        ('GRN', 'green'),
        ('BL', 'blue'),
    ))
    brend = models.CharField(max_length=10, default='wood')
    owner = models.ForeignKey(Rabbit, on_delete=models.CASCADE, null=True, blank=True)


class Silk(models.Model):
    color = models.CharField(max_length=20)
    hat = models.ForeignKey(Hat, on_delete=models.CASCADE)


class Door(models.Model):
    hole = models.ForeignKey(Hole, on_delete=models.CASCADE)
    owner = models.ForeignKey(Rabbit, on_delete=models.CASCADE, null=True, blank=True)
    size = models.PositiveIntegerField()


class Number(models.Model):
    doors = models.ManyToManyField(Door)
    wtf = models.ManyToManyField('self')


class ColorNumber(Number):
    color = models.CharField(max_length=20)


class Client(models.Model):
    username = models.CharField(max_length=20)
    city = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=50)


class Message(models.Model):
    content = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


class Tag(models.Model):
    title = models.CharField(max_length=20)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    messages = models.ManyToManyField(Message, null=True, blank=True)


class PointB(models.Model):
    pass


class PointA(models.Model):
    other = models.ManyToManyField("django_app.PointB",
                                   through="django_app.Through")


class Through(models.Model):
    pointas = models.ForeignKey(PointA, on_delete=models.CASCADE)
    pointbs = models.ForeignKey(PointB, on_delete=models.CASCADE)


class Simple(models.Model):
    value = models.IntegerField()
