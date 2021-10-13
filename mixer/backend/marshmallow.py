"""Support for Marshmallow.

::

    from mixer.backend.marshmallow import mixer


"""
from __future__ import absolute_import

import datetime as dt
import decimal
import typing

from marshmallow import fields, validate, missing, ValidationError

from .. import mix_types as t
from ..main import (
    TypeMixer as BaseTypeMixer, Mixer as BaseMixer, GenFactory as BaseFactory,
    LOGGER, faker, partial, SKIP_VALUE)


def get_nested(_scheme=None, _typemixer=None, _many=False, **kwargs):
    """Create nested objects."""
    obj = TypeMixer(
        _scheme,
        mixer=_typemixer._TypeMixer__mixer,
        factory=_typemixer._TypeMixer__factory,
        fake=_typemixer._TypeMixer__fake,
    ).blend(**kwargs)

    if _many:
        obj = [obj]

    return _scheme().dump(obj, many=_many)


class GenFactory(BaseFactory):
    """Support for Marshmallow fields."""

    types = {
        (fields.Str, fields.String): str,
        fields.UUID: t.UUID,
        (fields.Number, fields.Integer, fields.Int): t.BigInteger,
        fields.Decimal: decimal.Decimal,
        (fields.Bool, fields.Boolean): bool,
        fields.Float: float,
        #  (fields.DateTime, fields.AwareDateTime): dt.datetime,
        fields.Time: dt.time,
        fields.Date: dt.date,
        (fields.URL, fields.Url): t.URL,
        fields.Email: t.EmailString,
        # fields.FormattedString
        # fields.TimeDelta
        fields.Dict: dict,
        fields.Raw: typing.Any,
        # fields.Method
        # fields.Function
        # fields.Constant
    }

    generators = {
        fields.DateTime: lambda: faker.date_time().isoformat(),
        fields.AwareDateTime: lambda: faker.date_time().isoformat(),
        fields.Nested: get_nested,
    }


class TypeMixer(BaseTypeMixer):

    """ TypeMixer for Marshmallow. """

    factory = GenFactory

    def __load_fields(self):
        for name, field in self.__scheme._declared_fields.items():
            name = field.data_key if field.data_key is not None else name
            yield name, t.Field(field, name)

    def is_required(self, field):
        """ Return True is field's value should be defined.

        :return bool:

        """
        return field.scheme.required or (
            self.__mixer.params['required'] and not field.scheme.dump_only)

    @staticmethod
    def get_default(field):
        """ Get default value from field.

        :return value:

        """
        return field.scheme.dump_default is missing and SKIP_VALUE or field.scheme.dump_default # noqa

    def populate_target(self, values):
        """ Populate target. """
        try:
            return self.__scheme().load(dict(values))
        except ValidationError as exc:
            LOGGER.error("Mixer-marshmallow: %r", exc.messages)
            return

    def make_fabric(self, field, field_name=None, fake=False, kwargs=None): # noqa
        kwargs = {} if kwargs is None else kwargs

        if isinstance(field, fields.Nested):
            kwargs.update({'_typemixer': self, '_scheme': type(field.schema), '_many': field.many})

        if isinstance(field, fields.List):
            fab = self.make_fabric(
                field.inner, field_name=field_name, fake=fake, kwargs=kwargs)
            return lambda: [fab() for _ in range(faker.small_positive_integer(4))]

        for validator in field.validators:
            if isinstance(validator, validate.OneOf):
                return partial(faker.random_element, validator.choices)

        return super(TypeMixer, self).make_fabric(
            type(field), field_name=field_name, fake=fake, kwargs=kwargs)


class Mixer(BaseMixer):

    """ Integration with Marshmallow. """

    type_mixer_cls = TypeMixer

    def __init__(self, *args, **kwargs):
        super(Mixer, self).__init__(*args, **kwargs)

        # All fields is required by default
        self.params.setdefault('required', True)


mixer = Mixer()
