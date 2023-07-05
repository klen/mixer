from contextlib import suppress
from datetime import date, datetime, time
from decimal import Decimal
from typing import Callable, Optional, Type
from uuid import UUID

import peewee as pw

from mixer import database as db
from mixer import types as mt

from . import map_type, register
from .constants import FAKER
from .helpers import make_fields, make_gen
from .utils import defaultable

map_type(pw.AutoField, mt.SQLSerial)
map_type(pw.BigAutoField, mt.SQLBigSerial)
map_type(pw.IdentityField, mt.SQLSerial)

map_type(pw.IntegerField, mt.Int32)
map_type(pw.BigIntegerField, mt.Int64)
map_type(pw.SmallIntegerField, mt.Int16)
map_type(pw.FloatField, float)
map_type(pw.DoubleField, float)
map_type(pw.DecimalField, Decimal)
map_type(pw.CharField, str)
map_type(pw.FixedCharField, str)
map_type(pw.TextField, str)
map_type(pw.BlobField, bytes)
map_type(pw.BitField, mt.UInt16)
map_type(pw.UUIDField, UUID)
map_type(pw.BinaryUUIDField, UUID)
map_type(pw.DateTimeField, datetime)
map_type(pw.DateField, date)
map_type(pw.TimeField, time)
map_type(pw.TimestampField, mt.Timestamp)
map_type(pw.IPField, mt.IP4)
map_type(pw.BooleanField, bool)

with suppress(ImportError):
    from playhouse.postgres_ext import BinaryJSONField, JSONField

    map_type(JSONField, mt.JSON)
    map_type(BinaryJSONField, mt.JSON)

# TODO: Defered FK


@register(pw.Model)
def model_factory(
    ftype: Type[pw.Model], *, name=None, commit: bool = False, **params
) -> Callable[..., pw.Model]:
    meta = ftype._meta  # type: ignore[]
    generators = {
        name: factory_pw_field(field, name=name, commit=commit, **params)
        for name, field in meta.fields.items()
        if not (commit and isinstance(field, pw.AutoField))
    }

    def gen_pw_model(**values):
        fields = make_fields(values, generators)
        return ftype(**fields)

    return gen_pw_model


@register(pw.ForeignKeyField)
def fk_factory(ftype: Type[pw.ForeignKeyField], *, instance: pw.ForeignKeyField, **params):
    return model_factory(instance.rel_model, **params)


def factory_pw_field(field, **params) -> Optional[Callable]:
    """Get factory for the given field."""
    if not field.choices:
        gen = make_gen(field, **params)

    else:
        to_choice = [choice for choice, name in field.choices]
        gen = lambda **params: FAKER.random.choice(to_choice)  # noqa: E731

    if field.null:
        return defaultable(gen or (lambda: None), None)

    if field.default is not None:
        default = field.default() if callable(field.default) else field.default
        return defaultable(gen or (lambda: default), default)

    return gen


@db.register(pw.Model)
def commit(instance: pw.Model, **params):
    """Commit instance to the database."""
    for rel in instance.__rel__.values():
        if rel._pk is None:
            db.commit(rel)

    instance.save(force_insert=True)
    return instance


@db.register(pw.Model, "reload")
def reload(instance: pw.Model, **params):
    return instance.get_or_none(instance._pk_expr())  # type: ignore[]
