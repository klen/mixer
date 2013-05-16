from django.db import models


class Rabbit(models.Model):
    title = models.CharField(max_length=16)
    active = models.BooleanField()
    email = models.EmailField()

    created_at = models.DateField()
    updated_at = models.DateTimeField()

    opened_at = models.TimeField()
