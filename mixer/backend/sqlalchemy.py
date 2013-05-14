from __future__ import absolute_import
import datetime
import decimal

from ..main import (
    TypeMixer as BaseTypeMixer,
    Generator as BaseGenerator,
    Mixer as BaseMixer)
from ..generators import gen_small_integer
from sqlalchemy import Column
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


class TypeMixer(BaseTypeMixer):

    generator = Generator

    def __init__(self, cls, **params):
        super(TypeMixer, self).__init__(cls, **params)
        self.mapper = self.cls._sa_class_manager.mapper

    def set_value(self, target, column, fname, random=False, fake=False):
        if not isinstance(column, Column):
            return self.set_relation(target, column, fname,
                                     random=random, fake=fake)

        if not random and not fake:

            if column.default:
                return setattr(target, fname, column.default.arg)

            if column.nullable:
                return setattr(target, fname, None)

        return super(TypeMixer, self).set_value(target, column, fname,
                                                random, fake)

    @staticmethod
    def set_relation(target, relation, fname, random=False, fake=False,
                     params=None):
        params = params or dict()

        col = relation.local_remote_pairs[0][0]
        if col.nullable and not params:
            return None
        mixer = TypeMixer(relation.mapper.class_)
        value = mixer.blend(**params)

        setattr(target, col.name,
                relation.mapper.identity_key_from_instance(value)[1][0])
        setattr(target, fname, value)

    def make_generator(self, column, fname=None, fake=False):
        args = list()
        ftype = type(column.type)
        stype = self.generator.cls_to_simple(ftype)

        if stype is str:
            args.append(column.type.length)

        return self.generator.gen_maker(stype, fname, fake)(*args)

    def __load_fields(self):
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

# lint_ignore=W0212
