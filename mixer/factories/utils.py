from re import compile
from typing import Any, Callable, Final, Optional

from .constants import STR_TO_TYPE

TYPES_RE: Final = compile(r"(?P<type>\w+)\[(?P<args>.*)\]")


def is_typing(ftype):
    """Check if type is typing."""
    return getattr(ftype, "__module__", None) == "typing"


def find_type(ftype):
    """Convert string to type."""
    if not isinstance(ftype, str):
        return ftype

    tmatch = TYPES_RE.match(ftype)
    if tmatch:
        mtype = tmatch.group("type")
        if mtype == "Optional":
            return Optional[find_type(tmatch.group("args"))]

        return STR_TO_TYPE.get(tmatch.group("type"), str)

    return STR_TO_TYPE.get(ftype, str)


def defaultable(gen: Callable, default: Any = None):
    def wrapper(random: bool = False, **params):  # noqa:
        return gen(random=random, **params) if random else default

    return wrapper
