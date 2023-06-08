import datetime
from decimal import Decimal
from random import choice
from typing import Callable, Type

import sqlalchemy as sa
from sqlalchemy import orm

from mixer import database as db
from mixer import types as mt

from . import map_type, register
from .helpers import iterable_helper, make_fields, make_gen
from .utils import defaultable

MANYTOONE = orm.RelationshipDirection.MANYTOONE

map_type(sa.String, str)
map_type(sa.Text, str)
map_type(sa.Integer, mt.Int32)
map_type(sa.SmallInteger, mt.Int16)
map_type(sa.BigInteger, mt.Int64)
map_type(sa.Numeric, Decimal)
map_type(sa.Float, float)
map_type(sa.Double, float)
map_type(sa.DateTime, datetime.datetime)
map_type(sa.Date, datetime.date)
map_type(sa.Time, datetime.time)
map_type(sa.LargeBinary, bytes)
map_type(sa.Boolean, bool)
map_type(sa.Interval, datetime.timedelta)
map_type(sa.JSON, mt.JSON)

# TODO: PickleType, Tuple


@register(sa.Enum)
def factory_sa_enum(ftype: Type[sa.Enum], *, instance: sa.Enum, **params):
    choices = [v for k, v in instance._object_lookup.items() if k is not None]

    def gen(**params):
        return choice(choices)

    return gen


@register(sa.ARRAY)
def factory_sa_array(ftype: Type[sa.ARRAY], *, instance: sa.ARRAY, **params):
    return iterable_helper(list, instance.item_type)  # type: ignore[arg-type]


@register(orm.DeclarativeBase)
def factory_sa_model(
    ftype: Type[orm.DeclarativeBase], name=None, **params
) -> Callable[..., orm.DeclarativeBase]:
    mapper = ftype.__mapper__
    generators = {
        column.key: make_gen(column, name=column.key, **params) for column in mapper.columns
    }
    for rel in mapper.relationships:
        if rel.direction is not MANYTOONE:
            continue

        generators[rel.key] = factory_sa_model(rel.mapper.class_, **params)  # type: ignore[assignment]  # noqa: E501

    def gen_sqlalchemy_model(**values):
        fields = make_fields(values, generators)
        return ftype(**fields)

    return gen_sqlalchemy_model


@register(sa.Column)
def factory_sa_column(ftype: Type[sa.Column], *, instance: sa.Column, **params):
    gen = make_gen(instance.type, **params)

    if instance.nullable:
        return defaultable(gen or (lambda: None), None)  # type: ignore[return-value]

    if instance.default is not None:
        default = (
            instance.default.arg(None) if instance.default.is_callable else instance.default.arg  # type: ignore[attr-defined]  # noqa: E501
        )
        return defaultable(gen or (lambda: default), default)

    return gen


@db.register(orm.DeclarativeBase)
def commit(instance: orm.DeclarativeBase, *, session: orm.Session, **params):
    session.add(instance)
    session.commit()

    return instance


@db.register(orm.DeclarativeBase, "reload")
def reload(instance: orm.DeclarativeBase, *, session: orm.Session, **params):
    return session.merge(instance)
