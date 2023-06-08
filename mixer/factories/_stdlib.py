import datetime
from decimal import Decimal
from enum import Enum
from random import choice
from uuid import UUID

from . import register
from .constants import FAKER
from .types import TGen

# TODO: Support FAKE
# birthday from 18 to 65 years old


@register(datetime.date)
def factory_date(ftype, **params) -> TGen[datetime.date]:
    def gen_date(**params) -> datetime.date:
        return FAKER.date_object()

    return gen_date


@register(datetime.datetime)
def factory_datetime(ftype, **params) -> TGen[datetime.datetime]:
    def gen_datetime(**params) -> datetime.datetime:
        return FAKER.date_time()

    return gen_datetime


@register(datetime.time)
def factory_time(ftype, **params) -> TGen[datetime.time]:
    def gen_time(**params) -> datetime.time:
        return FAKER.time_object()

    return gen_time


@register(datetime.timedelta)
def factory_timedelta(ftype, **params) -> TGen[datetime.timedelta]:
    def gen_timedelta(**params) -> datetime.timedelta:
        return datetime.timedelta(seconds=FAKER.pyint(min_value=0, max_value=1000000))

    return gen_timedelta


@register(Decimal)
def factory_decimal(ftype, **params) -> TGen[Decimal]:
    def gen_decimal(**params) -> Decimal:
        return FAKER.pydecimal()

    return gen_decimal


@register(Enum)
def factory_enum(ftype, **params) -> TGen[Enum]:
    choices = list(ftype)

    def gen_enum(**params) -> Enum:
        return choice(choices)

    return gen_enum


@register(UUID)
def factory_uuid(ftype, **params) -> TGen[UUID]:
    def gen_uuid(**params) -> UUID:
        return FAKER.uuid4(cast_to=None)

    return gen_uuid
