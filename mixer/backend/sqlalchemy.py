from __future__ import absolute_import
import datetime
import decimal

from ..main import (
    TypeMixer as BaseTypeMixer,
    Generator as BaseGenerator,
    Mixer as BaseMixer)
from ..generators import gen_small_integer
from sqlalchemy import Column, func
from sqlalchemy.orm.interfaces import MANYTOONE
from sqlalchemy.types import (
    BIGINT, BOOLEAN, BigInteger, Boolean, CHAR, DATE, DATETIME, DECIMAL, Date,
    DateTime, FLOAT, Float, INT, INTEGER, Integer, NCHAR, NVARCHAR, NUMERIC,
    Numeric, SMALLINT, SmallInteger, String, TEXT, TIME, Text, Time, Unicode,
    UnicodeText, VARCHAR)


class Generator(BaseGenerator):
    types = {
        (String, VARCHAR, Unicode, NVARCHAR, NCHAR, CHAR, Text,
         UnicodeText, TEXT): str,
        (Boolean, BOOLEAN): bool,
        (Date, DATE): datetime.date,
        (DateTime, DATETIME): datetime.datetime,
        (Time, TIME): datetime.time,
        (DECIMAL, Numeric, NUMERIC): decimal.Decimal,
        (Float, FLOAT): float,
        (Integer, INTEGER, INT): int,
        (BigInteger, BIGINT): long,
        (SmallInteger, SMALLINT): gen_small_integer,
    }


LOAD = object()


class TypeMixer(BaseTypeMixer):

    generator = Generator
    load = LOAD

    def __init__(self, cls, **params):
        """ Init TypeMixer and save the mapper.
        """
        super(TypeMixer, self).__init__(cls, **params)
        self.mapper = self.cls._sa_class_manager.mapper

    def set_value(self, target, column, fname, random=False, fake=False,
                  select=False):
        if not isinstance(column, Column):
            return self.set_relation(target, column, fname,
                                     random=random, fake=fake, select=select)

        if not random and not fake:

            if (column.autoincrement and column.primary_key) \
                    or column.nullable:
                return False

            if column.default:
                default = column.default.arg(target) \
                    if column.default.is_callable \
                    else column.default.arg
                return setattr(target, fname, default)

        return super(TypeMixer, self).set_value(target, column, fname,
                                                random, fake)

    def set_relation(self, target, relation, fname, random=False, fake=False,
                     select=False, params=None):

        params = params or dict()

        # Select random instace from database
        if select and self.mixer and self.mixer.session:
            value = self.mixer.session.query(
                relation.mapper.class_
            ).order_by(func.random()).first()
            setattr(target, fname, value)
            return True

        if relation.direction == MANYTOONE:
            relname = relation.back_populates
            if relname and relation.mapper.get_property(relname):
                params[relname] = target

        col = relation.local_remote_pairs[0][0]
        if col.nullable and not params:
            return None

        mixer = TypeMixer(relation.mapper.class_)
        value = mixer.blend(**params)

        setattr(target, fname, value)
        setattr(target, col.name,
                relation.mapper.identity_key_from_instance(value)[1][0])

    def make_generator(self, column, fname=None, fake=False):
        """ Make values generator for column.

            :param column: SqlAlchemy column
            :param fname: Field name
            :param fake: Force fake data
        """
        args = list()
        ftype = type(column.type)
        stype = self.generator.cls_to_simple(ftype)

        if stype is str:
            args.append(column.type.length)

        return self.generator.gen_maker(stype, fname, fake)(*args)

    def __load_fields(self):
        """ Prepare TypeMixer.
            Select columns and relations for data generation.
        """
        mapper = self.cls._sa_class_manager.mapper
        relations = set()

        for rel in mapper.relationships:
            relations |= rel.local_columns
            yield rel.key, rel

        for column in mapper.columns:
            if not column in relations:
                yield column.name, column


class Mixer(BaseMixer):
    type_mixer_cls = TypeMixer

    def __init__(self, session=None, commit=False, **params):
        super(Mixer, self).__init__(**params)
        self.session = session
        assert not commit or self.session, "Set session for commits"
        self.commit = commit

    def blend(self, type_cls, **values):
        result = super(Mixer, self).blend(type_cls, **values)

        if self.commit:
            self.session.add(result)
            self.session.commit()

        return result

# lint_ignore=W0212
