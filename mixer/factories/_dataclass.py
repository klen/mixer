from dataclasses import MISSING, Field
from dataclasses import fields as dataclass_fields
from inspect import get_annotations
from typing import Callable, Optional

from . import register
from .helpers import make_fields, make_gen
from .utils import defaultable, find_type


def dataclass_factory(ftype, **params) -> Callable[..., object]:
    fields = dataclass_fields(ftype)
    try:
        ann = get_annotations(ftype, eval_str=True)
    except NameError:
        ann = get_annotations(ftype)

    generators = {
        field.name: make_gen(field, atype=find_type(ann.get(field.name)), name=field.name, **params)
        for field in fields
    }

    def gen_dataclass(**values):
        fields = make_fields(values, generators)
        return ftype(**fields)

    return gen_dataclass


@register(Field)
def dataclass_field_factory(ftype, *, instance: Field, atype=None, **params) -> Optional[Callable]:
    ftype = instance.type if isinstance(instance.type, type) else atype
    if ftype is None:
        return None

    gen = make_gen(ftype, **params)
    if gen is None:
        return None

    if instance.default is not MISSING:
        return defaultable(gen, instance.default)

    if instance.default_factory is not MISSING:
        default = instance.default_factory()
        return defaultable(gen, default)

    return gen
