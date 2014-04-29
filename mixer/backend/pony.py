""" Support for Pony ODM.

::

    from mixer.backend.pony import mixer
"""
from __future__ import absolute_import

from .. import mix_types as t

from pony.orm import PrimaryKey

from ..main import (
    TypeMixer as BaseTypeMixer, GenFactory as BaseFactory, Mixer as BaseMixer)


class GenFactory(BaseFactory):

    """ Map a Pony ORM classes to simple types. """

    types = {
        PrimaryKey: int,
    }


class TypeMixer(BaseTypeMixer):

    """ TypeMixer for Pony ORM. """

    factory = GenFactory

    def __load_fields(self):
        for attr in self.__scheme._attrs_:
            yield attr.column, t.Field(attr, attr.column)

    def populate_target(self, values):
        """ Populate target. """
        return self.__scheme(**dict(values))

    def is_required(self, field):
        """ Return True is field's value should be defined.

        :return bool:

        """
        return field.scheme.is_required and not field.scheme.is_pk

    def make_generator(self, field, field_name=None, fake=False, args=None, kwargs=None): # noqa
        """ Make values generator for column.

        :param column: SqlAlchemy column
        :param field_name: Field name
        :param fake: Force fake data

        :return generator:

        """
        py_type = field.py_type
        return super(TypeMixer, self).make_generator(
            py_type, field_name=field_name, fake=fake, args=args,
            kwargs=kwargs)


class Mixer(BaseMixer):

    """ Integration with Pony ORM. """

    type_mixer_cls = TypeMixer


# Default mixer
mixer = Mixer()
