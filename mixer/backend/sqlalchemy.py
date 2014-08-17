""" SQLAlchemy support. """
from __future__ import absolute_import

import datetime

import decimal
from sqlalchemy import func
# from sqlalchemy.orm.interfaces import MANYTOONE
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.types import (
    BIGINT, BOOLEAN, BigInteger, Boolean, CHAR, DATE, DATETIME, DECIMAL, Date,
    DateTime, FLOAT, Float, INT, INTEGER, Integer, NCHAR, NVARCHAR, NUMERIC,
    Numeric, SMALLINT, SmallInteger, String, TEXT, TIME, Text, Time, Unicode,
    UnicodeText, VARCHAR, Enum)

from .. import mix_types as t, generators as g
from ..main import (
    SKIP_VALUE, LOGGER, TypeMixer as BaseTypeMixer, GenFactory as BaseFactory,
    Mixer as BaseMixer, _Deffered)


class GenFactory(BaseFactory):

    """ Map a sqlalchemy classes to simple types. """

    types = {
        (String, VARCHAR, Unicode, NVARCHAR, NCHAR, CHAR): str,
        (Text, UnicodeText, TEXT): t.Text,
        (Boolean, BOOLEAN): bool,
        (Date, DATE): datetime.date,
        (DateTime, DATETIME): datetime.datetime,
        (Time, TIME): datetime.time,
        (DECIMAL, Numeric, NUMERIC): decimal.Decimal,
        (Float, FLOAT): float,
        (Integer, INTEGER, INT): int,
        (BigInteger, BIGINT): t.BigInteger,
        (SmallInteger, SMALLINT): t.SmallInteger,
    }


class TypeMixer(BaseTypeMixer):

    """ TypeMixer for SQLAlchemy. """

    factory = GenFactory

    def __init__(self, cls, **params):
        """ Init TypeMixer and save the mapper. """
        super(TypeMixer, self).__init__(cls, **params)
        self.mapper = self.__scheme._sa_class_manager.mapper

    def postprocess(self, target, postprocess_values):
        """ Fill postprocess values. """
        for name, deffered in postprocess_values:
            value = deffered.value
            if isinstance(getattr(target, name), InstrumentedList) and not isinstance(value, list):
                value = [value]
            setattr(target, name, value)

        if self.__mixer:
            target = self.__mixer.postprocess(target)

        return target

    @staticmethod
    def get_default(field):
        """ Get default value from field.

        :return value: A default value or NO_VALUE

        """
        column = field.scheme

        if isinstance(column, RelationshipProperty):
            column = column.local_remote_pairs[0][0]

        if not column.default:
            return SKIP_VALUE

        if column.default.is_callable:
            return column.default.arg(None)

        return getattr(column.default, 'arg', SKIP_VALUE)

    def gen_select(self, field_name, select):
        """ Select exists value from database.

        :param field_name: Name of field for generation.

        :return : None or (name, value) for later use

        """
        if not self.__mixer or not self.__mixer.params.get('session'):
            return field_name, SKIP_VALUE

        relation = self.mapper.get_property(field_name)
        session = self.__mixer.params.get('session')
        value = session.query(
            relation.mapper.class_
        ).filter(*select.choices).order_by(func.random()).first()
        return self.get_value(field_name, value)

    @staticmethod
    def is_unique(field):
        """ Return True is field's value should be a unique.

        :return bool:

        """
        scheme = field.scheme

        if isinstance(scheme, RelationshipProperty):
            scheme = scheme.local_remote_pairs[0][0]

        return scheme.unique

    @staticmethod
    def is_required(field):
        """ Return True is field's value should be defined.

        :return bool:

        """
        column = field.scheme
        if isinstance(column, RelationshipProperty):
            column = column.local_remote_pairs[0][0]

        return (
            bool(field.params)
            or not column.nullable
            and not (column.autoincrement and column.primary_key))

    def get_value(self, field_name, field_value):
        """ Get `value` as `field_name`.

        :return : None or (name, value) for later use

        """
        field = self.__fields.get(field_name)
        if field and isinstance(field.scheme, RelationshipProperty):
            return field_name, _Deffered(field_value, field.scheme)

        return super(TypeMixer, self).get_value(field_name, field_value)

    def make_generator(self, column, field_name=None, fake=False, args=None, kwargs=None): # noqa
        """ Make values generator for column.

        :param column: SqlAlchemy column
        :param field_name: Field name
        :param fake: Force fake data

        :return generator:

        """
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs

        if isinstance(column, RelationshipProperty):
            gen = g.loop(TypeMixer(
                column.mapper.class_, mixer=self.__mixer, fake=self.__fake,
                factory=self.__factory).blend)(**kwargs)
            return gen

        ftype = type(column.type)
        stype = self.__factory.cls_to_simple(ftype)

        if stype is str:
            kwargs['length'] = column.type.length

        if ftype is Enum:
            return g.gen_choice(column.type.enums)

        return super(TypeMixer, self).make_generator(
            stype, field_name=field_name, fake=fake, args=args, kwargs=kwargs)

    def guard(self, *args, **kwargs):
        """ Look objects in database.

        :returns: A finded object or False

        """
        try:
            session = self.__mixer.params.get('session')
            assert session
        except (AttributeError, AssertionError):
            raise ValueError('Cannot make request to DB.')

        qs = session.query(self.mapper).filter(*args, **kwargs)
        count = qs.count()

        if count == 1:
            return qs.first()

        if count:
            return qs.all()

        return False

    def reload(self, obj):
        """ Reload object from database. """
        try:
            session = self.__mixer.params.get('session')
            session.expire(obj)
            session.refresh(obj)
            return obj
        except (AttributeError, AssertionError):
            raise ValueError('Cannot make request to DB.')

    def __load_fields(self):
        """ Prepare SQLALchemyTypeMixer.

        Select columns and relations for data generation.

        """
        mapper = self.__scheme._sa_class_manager.mapper
        relations = set()
        if hasattr(mapper, 'relationships'):
            for rel in mapper.relationships:
                relations |= rel.local_columns
                yield rel.key, t.Field(rel, rel.key)

        for column in mapper.columns:
            if column not in relations:
                yield column.name, t.Field(column, column.name)


class Mixer(BaseMixer):

    """ Integration with SQLAlchemy. """

    type_mixer_cls = TypeMixer

    def __init__(self, session=None, commit=True, **params):
        """Initialize the SQLAlchemy Mixer.

        :param fake: (True) Generate fake data instead of random data.
        :param session: SQLAlchemy session. Using for commits.
        :param commit: (True) Commit instance to session after creation.

        """
        super(Mixer, self).__init__(**params)
        self.params['session'] = session
        self.params['commit'] = bool(session) and commit

    def postprocess(self, target):
        """ Save objects in db.

        :return value: A generated value

        """
        if self.params.get('commit'):
            session = self.params.get('session')
            if not session:
                LOGGER.warn("'commit' set true but session not initialized.")
            else:
                session.add(target)
                session.commit()

        return target


# Default mixer
mixer = Mixer()

# pylama:ignore=E1120
