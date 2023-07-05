import datetime
from decimal import Decimal
from enum import Enum
from typing import BinaryIO, Callable, Optional, Type
from uuid import UUID

import mongoengine as me
from bson.objectid import ObjectId

from mixer import database as db
from mixer import types as mt

from . import get_factory, map_type, register
from .constants import FAKER
from .helpers import make_fields, make_gen
from .utils import defaultable

map_type(me.StringField, str)
map_type(me.URLField, mt.URL)
map_type(me.EmailField, mt.Email)
map_type(me.IntField, mt.Int32)
map_type(me.LongField, mt.Int64)
map_type(me.FloatField, float)
map_type(me.DecimalField, Decimal)
map_type(me.BooleanField, bool)
map_type(me.DateTimeField, datetime.datetime)
map_type(me.DateField, datetime.date)
map_type(me.ComplexDateTimeField, datetime.datetime)
map_type(me.ListField, list)
map_type(me.DictField, dict)
map_type(me.BinaryField, bytes)
map_type(me.FileField, BinaryIO)
map_type(me.ImageField, BinaryIO)
map_type(me.SequenceField, mt.SQLSerial)
map_type(me.UUIDField, UUID)

# TODO: EmbeddedDocumentField, GenericEmbeddedDocumentField, DynamicField,
# EmbeddedDocumentListField, SortedListField, GeoPointField, Linestring, Polygon, Multipoint,
# Multiline, ...


register(me.ObjectIdField, ObjectId)


@register(me.EnumField)
def factory_me_enum(ftype: Type[me.EnumField], *, instance: me.EnumField, **params):
    enum = instance._enum_cls
    factory = get_factory(Enum, **params)
    return factory(enum)


@register(me.ReferenceField)
@register(me.CachedReferenceField)
def factory_me_rf(ftype: Type[me.ReferenceField], *, instance: me.ReferenceField, **params):
    document_type = instance.document_type
    if document_type is None:
        msg = "document_type is required for ReferenceField"
        raise ValueError(msg)
    return factory_me_document(document_type, **params)


@register(me.Document)
def factory_me_document(
    ftype: Type[me.Document], *, name=None, commit: bool = False, **params
) -> Callable[..., me.Document]:
    """Generate type value."""
    fields = ftype._fields  # type: ignore[]
    generators = {
        name: factory_me(field, name=name, commit=commit, **params)
        for name, field in fields.items()
        if not (commit and isinstance(field, me.ObjectIdField))
    }

    def gen_me_document(**values):
        fields = make_fields(values, generators)
        return ftype(**fields)

    return gen_me_document


def factory_me(field, **params) -> Optional[Callable]:
    """Get factory for the given field."""
    if not field.choices:
        gen = make_gen(field, **params)

    else:
        to_choice = [choice for choice, name in field.choices]
        gen = lambda **_: FAKER.random.choice(to_choice)  # noqa: E731

    if field.null:
        return defaultable(gen or (lambda: None), None)

    if field.default is not None:
        default = field.default() if callable(field.default) else field.default
        return defaultable(gen or (lambda: default), default)

    return gen


@db.register(me.Document)
def commit(instance: me.Document, **params):
    for field in instance._fields.values():  # type: ignore[]
        if isinstance(field, me.ReferenceField):
            assert field.name
            value = getattr(instance, field.name)
            if value is not None:
                value.save()

    instance.save()
    return instance


@db.register(me.Document, "reload")
def reload(instance: me.Document, **params):
    return instance.reload()
