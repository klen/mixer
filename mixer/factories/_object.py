from dataclasses import is_dataclass
from inspect import get_annotations
from typing import Callable, Optional, Type

from . import register
from ._dataclass import dataclass_factory
from .helpers import make_fields, make_gen
from .utils import defaultable, find_type


@register(object)
def object_factory(
    ftype: Type[object], *, name: Optional[str] = None, **params
) -> Callable[..., object]:
    """Generate type value."""
    # Support dataclasses
    if is_dataclass(ftype):
        return dataclass_factory(ftype, **params)

    try:
        fields = get_annotations(ftype, eval_str=True)
    except NameError:
        fields = get_annotations(ftype)

    generators = {
        name: make_gen(
            Field(find_type(fields[name]), default=getattr(ftype, name, ...)), name=name, **params
        )
        for name in fields
    }

    def gen_object(**values):
        instance = ftype()
        fields = make_fields(values, generators)
        for field, value in fields.items():
            setattr(instance, field, value)

        return instance

    return gen_object


class Field:
    __slots__ = ("ftype", "default")

    def __init__(self, ftype, default=...):
        self.ftype = ftype
        self.default = default


@register(Field)
def field_factory(ftype, *, instance: Field, **params) -> Optional[Callable]:
    ftype = instance.ftype
    gen = make_gen(ftype, **params)
    if gen is None:
        return None

    if instance.default is not ...:
        return defaultable(gen, instance.default)

    return gen
