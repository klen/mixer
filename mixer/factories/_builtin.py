from typing import Callable, Optional, Tuple, get_args, is_typeddict

from . import register
from ._typing import factory_typeddict
from .constants import FAKER, FLOAT_NAME_TO_FAKER, MAX_INT, STR_NAME_TO_FAKER
from .helpers import iterable_helper
from .types import TGen


@register(str)
def str_factory(
    ftype, *, fake=True, unique=False, max_length: int = 0, name: Optional[str] = None, **params
) -> TGen[str]:
    fmethod = "pystr"
    name = name.lower().strip() if fake and name else None
    fmethod = STR_NAME_TO_FAKER.get(name, fmethod) if name else fmethod

    def gen_str(**params) -> str:
        faker = FAKER.unique if unique else FAKER
        res = getattr(faker, fmethod)()
        return res[:max_length] if max_length else res

    return gen_str


def int_factory(
    ftype,
    *,
    unique: bool = False,
    min: int = 0 - MAX_INT,
    max: int = MAX_INT,
    fake: bool = True,
    name: Optional[str] = None,
    **params,
) -> TGen[int]:
    name = name.lower().strip() if fake and name else None

    def gen_int(**params) -> int:
        if name and name == "percent":
            return FAKER.random_int(min=0, max=100)

        return (
            FAKER.unique.random_int(min=min, max=max)
            if unique
            else FAKER.random_int(min=min, max=max)
        )

    return gen_int


register(int)(int_factory)  # no decorator because of mypy error


@register(float)
def float_factory(
    ftype, *, unique=False, fake=True, name: Optional[str] = None, **params
) -> TGen[float]:
    fmethod = "pyfloat"
    name = name.lower().strip() if fake and name else None
    fmethod = FLOAT_NAME_TO_FAKER.get(name, fmethod) if name else fmethod

    def gen_float(**params) -> float:
        faker = FAKER.unique if unique else FAKER
        return float(getattr(faker, fmethod)())

    return gen_float


@register(complex)
def complex_factory(ftype, *, unique=False, **params) -> TGen[complex]:
    def gen_complex(**params) -> complex:
        faker = FAKER.unique.pyfloat if unique else FAKER.pyfloat
        return complex(faker(positive=True), faker(positive=True))

    return gen_complex


@register(bool)
def bool_factory(ftype, **params) -> TGen[bool]:
    gen = FAKER.pybool
    return lambda **params: gen()


@register(bytes)
def factory_bytes(ftype, **params) -> TGen[bytes]:
    def gen_bytes(**params) -> bytes:
        return FAKER.pystr().encode()

    return gen_bytes


@register(tuple)
@register(Tuple)  # type: ignore[call-overload]
def tuple_factory(ftype, **params) -> TGen[tuple]:
    args = get_args(ftype)
    if not args:
        return lambda **params: FAKER.pytuple()

    return iterable_helper(tuple, args[0])


@register(dict)
def dict_factory(ftype, **params) -> TGen[dict]:
    # Support TypedDict
    if is_typeddict(ftype):
        td_gen = factory_typeddict(ftype, **params)
        register(ftype, td_gen)
        return td_gen

    args = get_args(ftype)
    if not args:
        return lambda **params: FAKER.pydict()

    key_type, value_type = args
    keys_gen = iterable_helper(tuple, key_type)
    values_gen = iterable_helper(tuple, value_type)

    def gen() -> dict:
        return dict(zip(keys_gen(), values_gen()))

    return gen


@register(list)
def list_factory(ftype: list, **params) -> Callable[..., list]:
    """Generate list value."""
    args = get_args(ftype)
    if not args:
        return lambda **params: FAKER.pylist()

    return iterable_helper(list, args[0])


@register(set)
def set_factory(ftype: set, **params) -> Callable[..., set]:
    """Generate set value."""
    args = get_args(ftype)
    if not args:
        return lambda **params: FAKER.pyset()

    return iterable_helper(set, args[0])
