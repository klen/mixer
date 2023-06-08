import datetime
from decimal import Decimal
from typing import Dict, List, Literal, Optional, Set, Tuple, TypedDict

import pytest

from mixer import mixer
from mixer import types as mt
from mixer.factories import FACTORIES


def test_str():
    res = mixer.blend(str)
    assert res
    assert isinstance(res, str)


def test_int():
    res = mixer.blend(int)
    assert res is not None
    assert isinstance(res, int)


def test_float():
    res = mixer.blend(float)
    assert res is not None
    assert isinstance(res, float)


def test_complex():
    res = mixer.blend(complex)
    assert res is not None
    assert isinstance(res, complex)


def test_bool():
    res = mixer.blend(bool)
    assert res is not None
    assert isinstance(res, bool)


def test_bytes():
    res = mixer.blend(bytes)
    assert res is not None
    assert isinstance(res, bytes)


def test_tuple():
    res = mixer.blend(tuple)
    assert res is not None
    assert isinstance(res, tuple)

    res = mixer.blend(Tuple)
    assert res is not None
    assert isinstance(res, tuple)

    res = mixer.blend(Tuple[int, ...])
    assert res is not None
    assert isinstance(res, tuple)
    assert all(isinstance(x, int) for x in res)


def test_dict():
    res = mixer.blend(dict)
    assert res is not None
    assert isinstance(res, dict)

    res = mixer.blend(Dict)
    assert res is not None
    assert isinstance(res, dict)

    res = mixer.blend(Dict[str, float])
    assert res is not None
    assert isinstance(res, dict)
    assert all(isinstance(x, str) for x in res)
    assert all(isinstance(x, float) for x in res.values())


def test_list():
    res = mixer.blend(list)
    assert res is not None
    assert isinstance(res, list)

    res = mixer.blend(List)
    assert res is not None
    assert isinstance(res, list)

    res = mixer.blend(List[str])
    assert res is not None
    assert isinstance(res, list)
    assert all(isinstance(x, str) for x in res)


def test_set():
    res = mixer.blend(set)
    assert res is not None
    assert isinstance(res, set)

    res = mixer.blend(Set)
    assert res is not None
    assert isinstance(res, set)

    res = mixer.blend(Set[bytes])
    assert res is not None
    assert isinstance(res, set)
    assert all(isinstance(x, bytes) for x in res)


def test_decimal():
    res = mixer.blend(Decimal)
    assert res
    assert isinstance(res, Decimal)


def test_date():
    res = mixer.blend(datetime.date)
    assert res
    assert isinstance(res, datetime.date)


def test_datetime():
    res = mixer.blend(datetime.datetime)
    assert res
    assert isinstance(res, datetime.datetime)


def test_time():
    res = mixer.blend(datetime.time)
    assert res
    assert isinstance(res, datetime.time)


def test_timedelta():
    res = mixer.blend(datetime.timedelta)
    assert res
    assert isinstance(res, datetime.timedelta)


def test_enum():
    from enum import Enum

    class MyEnum(Enum):
        A = 1
        B = 2

    res = mixer.blend(MyEnum)
    assert res
    assert isinstance(res, MyEnum)


def test_uuid():
    from uuid import UUID

    res = mixer.blend(UUID)
    assert res
    assert isinstance(res, UUID)


@pytest.mark.parametrize("ftype", [Optional, Optional[int]])
def test_optional(ftype):
    res = mixer.blend(ftype)
    assert res is None or isinstance(res, int)


def test_literal():
    res = mixer.blend(Literal["a", "b", "c"])
    assert res in ["a", "b", "c"]


def test_typeddict():
    class Movie(TypedDict):
        name: str
        year: int

    res = mixer.blend(Movie)
    assert res
    assert isinstance(res, dict)
    assert isinstance(res["name"], str)
    assert isinstance(res["year"], int)

    res = mixer.blend(Movie)
    assert res

    assert Movie in FACTORIES
    res = FACTORIES[Movie](Movie)()
    assert res


def test_mixer_types():
    res = mixer.blend(mt.Int8)
    assert -128 <= res <= 127

    res = mixer.blend(mt.Int16)
    assert -32768 <= res <= 32767

    res = mixer.blend(mt.Int32)
    assert -2147483648 <= res <= 2147483647

    res = mixer.blend(mt.Int64)
    assert -9223372036854775808 <= res <= 9223372036854775807

    res = mixer.blend(mt.UInt16)
    assert 0 <= res <= 65535

    res = mixer.blend(mt.UInt32)
    assert 0 <= res <= 4294967295

    res = mixer.blend(mt.SQLSerial)
    assert 0 <= res <= 2147483647

    res = mixer.blend(mt.SQLBigSerial)
    assert 0 <= res <= 9223372036854775807

    res = mixer.blend(mt.Timestamp)
    assert 0 <= res <= 2147483647

    res = mixer.blend(mt.IP4)
    assert "." in res

    res = mixer.blend(mt.IP6)
    assert ":" in res

    res = mixer.blend(mt.Email)
    assert "@" in res

    res = mixer.blend(mt.FilePath)
    assert "/" in res

    res = mixer.blend(mt.URL)
    assert "/" in res

    res = mixer.blend(mt.JSON)
    assert res


def test_fake_str():
    from mixer.factories._builtin import STR_NAME_TO_FAKER, str_factory

    for name in STR_NAME_TO_FAKER:
        gen = str_factory(str, name=name)
        res = gen()
        assert res
        assert isinstance(res, str)


def test_fake_float():
    from mixer.factories._builtin import FLOAT_NAME_TO_FAKER, float_factory

    for name in FLOAT_NAME_TO_FAKER:
        gen = float_factory(float, name=name)
        res = gen()
        assert res
        assert isinstance(res, float)
