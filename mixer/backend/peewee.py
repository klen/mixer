""" Support for Peewee ODM.

::

    from mixer.backend.peewee import mixer

"""
from __future__ import absolute_import

from peewee import * # noqa
import datetime
import decimal

from .. import mix_types as t
from ..main import (
    TypeMixer as BaseTypeMixer, Mixer as BaseMixer, SKIP_VALUE,
    GenFactory as BaseFactory)


def get_relation(_scheme=None, _typemixer=None, **params):
    """ Function description. """
    scheme = _scheme.rel_model

    return TypeMixer(
        scheme,
        mixer=_typemixer._TypeMixer__mixer,
        factory=_typemixer._TypeMixer__factory,
        fake=_typemixer._TypeMixer__fake,
    ).blend(**params)


def get_blob(**kwargs):
    """ Generate value for BlobField. """
    raise NotImplementedError


class GenFactory(BaseFactory):

    """ Map a peewee classes to simple types. """

    types = {
        PrimaryKeyField: t.PositiveInteger,
        IntegerField: int,
        BigIntegerField: t.BigInteger,
        (FloatField, DoubleField): float,
        DecimalField: decimal.Decimal,
        CharField: str,
        TextField: t.Text,
        DateTimeField: datetime.datetime,
        DateField: datetime.date,
        TimeField: datetime.time,
        BooleanField: bool,
        # BlobField: None,
    }

    generators = {
        BlobField: get_blob,
        ForeignKeyField: get_relation,
    }


class TypeMixer(BaseTypeMixer):

    """ TypeMixer for Pony ORM. """

    factory = GenFactory

    def __load_fields(self):
        for name, field in self.__scheme._meta.get_sorted_fields():
            yield name, t.Field(field, name)

    def populate_target(self, values):
        """ Populate target. """
        return self.__scheme(**dict(values))

    def gen_field(self, field):
        """ Function description. """
        if isinstance(field.scheme, PrimaryKeyField)\
                and self.__mixer and self.__mixer.params.get('commit'):
            return field.name, SKIP_VALUE
        return super(TypeMixer, self).gen_field(field)

    def is_required(self, field):
        """ Return True is field's value should be defined.

        :return bool:

        """
        return not field.scheme.null

    def is_unique(self, field):
        """ Return True is field's value should be a unique.

        :return bool:

        """
        return field.scheme.unique

    @staticmethod
    def get_default(field):
        """ Get default value from field.

        :return value:

        """
        return field.scheme.default is None and SKIP_VALUE or field.scheme.default # noqa

    def make_generator(self, field, field_name=None, fake=False, args=None, kwargs=None): # noqa
        """ Make values generator for column.

        :param column: SqlAlchemy column
        :param field_name: Field name
        :param fake: Force fake data

        :return generator:

        """
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs

        if isinstance(field, ForeignKeyField):
            kwargs.update({'_typemixer': self, '_scheme': field})

        return super(TypeMixer, self).make_generator(
            type(field), field_name=field_name, fake=fake, args=args,
            kwargs=kwargs)


class Mixer(BaseMixer):

    """ Integration with Pony ORM. """

    type_mixer_cls = TypeMixer

    def postprocess(self, target):
        """ Save objects in db.

        :return value: A generated value

        """
        if self.params.get('commit'):
            target.save()

        return target


# Default Pony mixer
mixer = Mixer()

# pylama:ignore=E1120
