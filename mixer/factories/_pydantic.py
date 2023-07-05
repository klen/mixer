from typing import Callable

from pydantic import v1

from . import register
from .helpers import make_fields, make_gen
from .utils import defaultable


@register(v1.BaseModel)
def model_factory(ftype, name=None, **params) -> Callable[..., v1.BaseModel]:
    """Generate type value."""
    fields = ftype.__fields__
    generators = {name: make_gen(field, name=name, **params) for name, field in fields.items()}

    def gen_pydantic(**values):
        fields = make_fields(values, generators)
        return ftype(**fields)

    return gen_pydantic


@register(v1.fields.ModelField)
def field_factory(ftype, *, instance: v1.fields.ModelField, **params):
    ftype = instance.annotation
    gen = make_gen(ftype, **params)

    if instance.allow_none:
        return defaultable(gen or (lambda: None), None)

    if not instance.required:
        return defaultable(gen or (lambda: None), instance.get_default())

    return make_gen(instance.annotation, **params)
