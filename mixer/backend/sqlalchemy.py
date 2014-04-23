""" SQLAlchemy support. """
from __future__ import absolute_import

import datetime

import decimal
from sqlalchemy import func
# from sqlalchemy.orm.interfaces import MANYTOONE
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.types import (
    BIGINT, BOOLEAN, BigInteger, Boolean, CHAR, DATE, DATETIME, DECIMAL, Date,
    DateTime, FLOAT, Float, INT, INTEGER, Integer, NCHAR, NVARCHAR, NUMERIC,
    Numeric, SMALLINT, SmallInteger, String, TEXT, TIME, Text, Time, Unicode,
    UnicodeText, VARCHAR, Enum)

from .. import mix_types as t, generators as g
from ..main import (
    NO_VALUE, LOGGER, TypeMixer as BaseTypeMixer, GenFactory as BaseFactory,
    Mixer as BaseMixer)


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

    @staticmethod
    def get_default(field, target):
        """ Get default value from field.

        :return value: A default value or NO_VALUE

        """
        column = field.scheme

        if isinstance(column, RelationshipProperty):
            column = column.local_remote_pairs[0][0]

        if not column.default:
            return NO_VALUE

        if column.default.is_callable:
            return column.default.arg(target)

        return getattr(column.default, 'arg', NO_VALUE)

    def gen_select(self, target, field_name, select):
        """ Select exists value from database.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.

        :return : None or (name, value) for later use

        """
        if not self.__mixer or not self.__mixer.params.get('session'):
            return False

        relation = self.mapper.get_property(field_name)
        session = self.__mixer.params.get('session')
        value = session.query(
            relation.mapper.class_
        ).filter(*select.choices).order_by(func.random()).first()
        self.set_value(target, field_name, value)

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

    def set_value(self, target, field_name, field_value, finaly=False):
        """ Set `value` to `target` as `field_name`.

        :return : None or (name, value) for later use

        """
        field = self.__fields.get(field_name)
        if field and isinstance(field.scheme, RelationshipProperty):
            col = field.scheme.local_remote_pairs[0][0]
            setattr(
                target, col.name,
                field.scheme.mapper.identity_key_from_instance(
                    field_value)[1][0])

        return super(TypeMixer, self).set_value(
            target, field_name, field_value, finaly)

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
        stype = self.factory.cls_to_simple(ftype)

        if stype is str:
            kwargs['length'] = column.type.length

        if ftype is Enum:
            return g.gen_choice(column.type.enums)

        return super(TypeMixer, self).make_generator(
            stype, field_name=field_name, fake=fake, args=args, kwargs=kwargs)

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

    def post_generate(self, result):
        """ Save objects in db.

        :return value: A generated value

        """
        if self.params.get('commit'):
            session = self.params.get('session')
            if not session:
                LOGGER.warn("'commit' set true but session not initialized.")
            else:
                session.add(result)
                # Use transaction manager when needed
                try:
                    session.commit()
                except AssertionError:
                    import transaction as tm
                    tm.commit()

        return result


# Default mixer
mixer = Mixer()

# lint_ignore=W0212,E1002
