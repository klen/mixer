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
    GenFactory as BaseFactory, partial, faker)


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

    """ TypeMixer for Peewee ORM. """

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

    def make_fabric(self, field, field_name=None, fake=False, kwargs=None): # noqa
        """ Make values fabric for column.

        :param column: SqlAlchemy column
        :param field_name: Field name
        :param fake: Force fake data

        :return function:

        """
        kwargs = {} if kwargs is None else kwargs

        if field.choices:
            try:
                choices, _ = list(zip(*field.choices))
                return partial(faker.random_element, choices)
            except ValueError:
                pass

        if isinstance(field, ForeignKeyField):
            kwargs.update({'_typemixer': self, '_scheme': field})

        return super(TypeMixer, self).make_fabric(
            type(field), field_name=field_name, fake=fake, kwargs=kwargs)

    def guard(self, *args, **kwargs):
        """ Look objects in database.

        :returns: A finded object or False

        """
        qs = self.__scheme.select().where(*args, **kwargs)
        count = qs.count()

        if count == 1:
            return qs.get()

        if count:
            return list(qs)

        return False

    def reload(self, obj):
        """ Reload object from database. """
        if not obj.get_id():
            raise ValueError("Cannot load the object: %s" % obj)
        return type(obj).select().where(obj._meta.primary_key == obj.get_id()).get()


class Mixer(BaseMixer):

    """ Integration with Peewee ORM. """

    type_mixer_cls = TypeMixer

    def postprocess(self, target):
        """ Save objects in db.

        :return value: A generated value

        """
        if self.params.get('commit'):
            target.save()

        return target


# Default Peewee mixer
mixer = Mixer()

# pylama:ignore=E1120
