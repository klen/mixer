""" Support for Yet Another Document Mapper (YADM). """
from __future__ import absolute_import

import datetime
import decimal
from bson import ObjectId
from yadm import Document
from yadm.fields import (
    BooleanField, DecimalField, FloatField, IntegerField, StringField, EmailField,
    ListField, SetField, ObjectIdField, ReferenceField, DatetimeField, EmbeddedDocumentField)
from yadm.markers import NoDefault

from .. import mix_types as t, generators as gen
from ..main import TypeMixer as BaseTypeMixer, GenFactory as BaseFactory,\
    Mixer as BaseMixer, SKIP_VALUE, partial


def get_list_field(_typemixer, _scheme):
    fab = _typemixer.make_generator(_scheme.item_field)
    return lambda: [fab() for _ in range(3)]


def get_set_field(**kwargs):
    return set(get_list_field(**kwargs))


def get_objectid(*args, **kwargs):
    """ Create a new ObjectId instance.

    :return ObjectId:

    """
    return ObjectId()


class GenFactory(BaseFactory):

    """ Map a mongoengine classes to simple types. """

    types = {
        BooleanField: bool,
        DatetimeField: datetime.datetime,
        DecimalField: decimal.Decimal,
        EmailField: t.EmailString,
        FloatField: float,
        IntegerField: int,
        StringField: str,
    }

    generators = {
        ListField: get_list_field,
        SetField: get_set_field,
        ObjectIdField: get_objectid,
    }


class TypeMixer(BaseTypeMixer):

    """ TypeMixer for YADM. """

    factory = GenFactory

    def __load_fields(self):
        for fname, field in self.__scheme.__fields__.items():
            yield fname, t.Field(field, fname)

    @staticmethod
    def get_default(field):
        """ Get default value from field.

        :return value: A default value or NO_VALUE

        """
        if field.scheme.default is NoDefault:
            return SKIP_VALUE

        if callable(field.scheme.default):
            return field.scheme.default()

        return field.scheme.default

    @staticmethod
    def is_required(field):
        """ Return True is field's value should be defined.

        :return bool:

        """
        return True

    def make_generator(self, yadm_field, field_name=None, fake=None, kwargs=None): # noqa
        """ Make values generator for field.

        :param yadm_field: YADM field's instance
        :param field_name: Field name
        :param fake: Force fake data

        :return generator:

        """
        ftype = type(yadm_field)
        kwargs = {} if kwargs is None else kwargs

        if getattr(yadm_field, 'choices', None):
            if isinstance(yadm_field.choices[0], tuple):
                choices, _ = list(zip(*yadm_field.choices))
            else:
                choices = list(yadm_field.choices)

            return partial(gen.get_choice, choices)

        elif isinstance(yadm_field, ReferenceField):
            ftype = yadm_field.reference_document_class

        elif isinstance(yadm_field, EmbeddedDocumentField):
            ftype = yadm_field.embedded_document_class

        elif ftype is DecimalField:
            sign, (ii,), dd = yadm_field.precision.as_tuple()
            kwargs['d'] = abs(dd)
            kwargs['positive'] = not sign
            kwargs['i'] = ii + 1

        elif ftype in (SetField, ListField):
            kwargs.update({'_typemixer': self, '_scheme': yadm_field})

        return super(TypeMixer, self).make_generator(
            ftype, field_name=field_name, fake=fake, kwargs=kwargs)


class Mixer(BaseMixer):

    """ Mixer class for YADM. """

    type_mixer_cls = TypeMixer

    def __init__(self, db=None, **params):
        """ Initialize the YADM Mixer.

        :param fake: (True) Generate fake data instead of random data.
        :param commit: (True) Save object to Mongo DB.

        """
        super(Mixer, self).__init__(**params)
        self.params['db'] = db

    def postprocess(self, target):
        """ Save instance to DB.

        :return instance:

        """
        db = self.params.get('db')
        if db and isinstance(target, Document):
            db.insert(target)

        return target


mixer = Mixer()

# pylama:ignore=D,E1120,F0401
