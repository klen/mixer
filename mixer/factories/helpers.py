from collections import defaultdict
from inspect import isclass
from types import GeneratorType
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union, get_origin

from . import FACTORIES
from .constants import RANDOM, SKIP
from .types import TV
from .utils import is_typing


def make_gen(ftype: Union[TV, Type[TV]], **params) -> Optional[Callable[..., TV]]:
    """Get generator for the given type."""
    if ftype in FACTORIES:
        return FACTORIES[ftype](ftype=ftype, **params)

    if not isclass(ftype) and not is_typing(ftype):
        params["instance"] = ftype
        ftype = type(ftype)  # type: ignore[assignment]

    origin = get_origin(ftype)
    factory = FACTORIES.get(origin or ftype)

    if factory:
        return factory(ftype=ftype, **params)

    for ctype in ftype.mro():  # type: ignore[union-attr]
        if ctype in FACTORIES:
            factory = FACTORIES[ctype]
            break

    if factory is not None:
        FACTORIES[ftype] = factory
        return factory(ftype=ftype, **params)

    return None


def iterable_helper(ftype: Type[TV], fctype: Type) -> Callable[..., TV]:
    """Generate iterable value."""
    generator = make_gen(fctype)
    if generator is None:
        error_message = f"Unsupported type: {fctype}"
        raise ValueError(error_message)

    def gen(length=5):
        gen = generator
        return ftype(gen() for _ in range(length))

    return gen


def split_values(values: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    nested_values: defaultdict = defaultdict(dict)
    for field in list(values.keys()):
        nested, _, nfield = field.partition("__")
        if nfield:
            nested_values[nested][nfield] = values.pop(field)

    return values, nested_values


def make_fields(
    values: Dict[str, Any], generators: Dict[str, Optional[Callable]]
) -> Dict[str, Any]:
    fields = {}
    values, nested_values = split_values(values)
    for field_name, gen in generators.items():
        if gen is None:
            continue

        value = values.get(field_name, ...)
        nparams = nested_values.get(field_name, {})
        if value is RANDOM:
            fields[field_name] = gen(random=True, **nparams)

        elif value is ...:
            fields[field_name] = gen(**nested_values.get(field_name, {}))

    for field, value in values.items():
        if value in (SKIP, RANDOM):
            continue

        # Support generators
        try:
            fields[field] = next(value) if isinstance(value, GeneratorType) else value
        except StopIteration as err:  # noqa: PERF203
            msg = f"Generator value for '{field}' is empty"
            raise ValueError(msg) from err

    return fields
