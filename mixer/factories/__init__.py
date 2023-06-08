from contextlib import suppress
from typing import Any, Callable, Dict, Final, Optional, Type, overload

from .types import TV, TFactory, TGen

FACTORIES: Final[Dict[Any, TFactory]] = {}


@overload
def register(ftype) -> Callable[[TV], TV]:
    ...


@overload
def register(ftype, gen: TGen[TV]) -> TGen[TV]:
    ...


def register(ftype, gen=None):
    """Register factory for type."""

    if gen is not None:
        FACTORIES[ftype] = lambda ftype, **params: gen  # type: ignore[assignment]
        return gen

    def wrapper(factory: TFactory[TV]) -> TFactory[TV]:
        FACTORIES[ftype] = factory
        return factory

    return wrapper


def map_type(source: type, target: type) -> Callable[..., Callable]:
    """Map source type to target type."""
    if target not in FACTORIES:
        msg = f"Target type {target} is not supported"
        raise ValueError(msg)

    FACTORIES[source] = FACTORIES[target]
    return FACTORIES[source]


def get_factory(ftype: type) -> TFactory:
    """Get factory for the given type."""
    return FACTORIES[ftype]


from ._builtin import *
from ._mixer import *
from ._object import *
from ._stdlib import *
from ._typing import *

with suppress(ImportError):
    from . import _peewee

with suppress(ImportError):
    from . import _peewee_aio

with suppress(ImportError):
    from . import _pydantic

with suppress(ImportError):
    from . import _django

with suppress(ImportError):
    from . import _mongoengine

with suppress(ImportError):
    from . import _sqlalchemy


# ruff: noqa: E402,F401,F403
