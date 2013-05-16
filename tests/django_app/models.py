from django.db import models


class Rabbit(models.Model):
    title = models.CharField(max_length=16)
