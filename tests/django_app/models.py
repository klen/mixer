from django.db import models


class Rabbit(models.Model):
    title = models.CharField(max_length=16)
    active = models.BooleanField()
    email = models.EmailField()

    created_at = models.DateField()
    updated_at = models.DateTimeField()

    opened_at = models.TimeField()
    percent = models.FloatField()
    money = models.IntegerField()
    ip = models.IPAddressField()


class Hole(models.Model):
    title = models.CharField(max_length=16)
    owner = models.ForeignKey(Rabbit)
