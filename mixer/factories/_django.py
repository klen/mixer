from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Callable, Optional
from uuid import UUID

from django.db import models

from mixer import database as db
from mixer import types as mt

from . import map_type, register
from .constants import FAKER
from .helpers import make_fields, make_gen
from .utils import defaultable

map_type(models.BooleanField, bool)
map_type(models.CharField, str)
map_type(models.DateField, date)
map_type(models.DateTimeField, datetime)
map_type(models.DecimalField, Decimal)
map_type(models.DurationField, timedelta)
map_type(models.EmailField, mt.Email)
map_type(models.FilePathField, mt.FilePath)
map_type(models.FloatField, float)
map_type(models.IntegerField, mt.Int32)
map_type(models.BigIntegerField, mt.Int64)
map_type(models.SmallIntegerField, mt.Int16)
map_type(models.GenericIPAddressField, mt.IP4)
map_type(models.PositiveBigIntegerField, mt.UInt64)
map_type(models.PositiveIntegerField, mt.UInt32)
map_type(models.PositiveSmallIntegerField, mt.UInt16)
map_type(models.SlugField, str)
map_type(models.TextField, str)
map_type(models.TimeField, time)
map_type(models.URLField, mt.URL)
map_type(models.BinaryField, bytes)
map_type(models.UUIDField, UUID)
map_type(models.AutoField, mt.SQLSerial)
map_type(models.BigAutoField, mt.SQLBigSerial)
map_type(models.SmallAutoField, mt.SQLSerial)


@register(models.ForeignKey)
def fk_factory(ftype, *, instance, **params):
    return model_factory(instance.related_model, **params)


@register(models.Model)
def model_factory(
    ftype, *, name=None, commit: bool = False, **params
) -> Callable[..., models.Model]:
    """Generate Django model."""
    opts = ftype._meta
    generators = {
        field.name: make_django_gen(field, name=field.name, commit=commit, **params)
        for field in opts.get_fields()
        if not (commit and isinstance(field, models.AutoField))
    }

    def gen_django_model(**values):
        instance = ftype()
        for name, value in make_fields(values, generators).items():
            setattr(instance, name, value)
        return instance

    return gen_django_model


def make_django_gen(field: models.Field, **params) -> Optional[Callable]:
    if isinstance(field, models.ForeignObjectRel):
        return None

    if not field.choices:
        gen = make_gen(field, **params)
    else:
        to_choice = [choice for choice, name in field.choices]
        gen = lambda: FAKER.random.choice(to_choice)  # noqa: E731

    if field.null:
        return defaultable(gen or (lambda: None), None)

    if field.default is not models.NOT_PROVIDED:
        default = field.get_default()
        return defaultable(gen or (lambda: default), default)

    return gen


@db.register(models.Model)
def commit(instance: models.Model, **params):
    opts = instance._meta  # type: ignore[]
    for field in opts.get_fields():
        if isinstance(field, models.ForeignKey):
            rel = getattr(instance, field.name)
            if rel is not None:
                db.commit(rel)

    instance.save(force_insert=True)
    return instance


@db.register(models.Model, "reload")
def reload(instance: models.Model, **params):
    return instance.__class__.objects.get(pk=instance.pk)  # type: ignore[]
