from pathlib import Path
from typing import Any, BinaryIO, Callable, Literal, Optional, TextIO, Union, get_args

from . import register
from .constants import FAKER
from .helpers import make_gen
from .types import TNone


@register(Union)
@register(Optional)
def factory_union(ftype, **params) -> Callable:
    """Generate union value."""
    args = get_args(ftype)
    if not args:
        return lambda: None

    is_optional = len(args) == 2 and args[1] is TNone
    generators = [make_gen(arg) for arg in args]

    def gen_union_value(*, random: bool = False, **params):
        gen = generators[0] if random and is_optional else FAKER.random_element(generators)
        return gen(**params) if gen else None

    return gen_union_value


@register(Literal)
def factory_literal(ftype, **params) -> Callable:
    """Generate literal value."""
    args = get_args(ftype)
    if not args:
        return lambda: None

    def gen_literal_value():
        return FAKER.random_element(args)

    return gen_literal_value


@register(BinaryIO)
def factory_binaryio(ftype, **params) -> Callable:
    """Generate binary file."""
    return lambda: Path(__file__).open("rb")


@register(TextIO)
def factory_textio(ftype, **params) -> Callable:
    """Generate binary file."""
    return lambda: Path(__file__).open("r")


def factory_typeddict(ftype, **params) -> Callable[..., dict[str, Any]]:
    """Generate typed dict."""
    generators = {k: make_gen(v) for k, v in ftype.__annotations__.items()}
    return lambda: {k: gen(**params) for k, gen in generators.items() if gen}
