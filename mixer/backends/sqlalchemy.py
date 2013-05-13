from __future__ import absolute_import
import datetime
import decimal

from ..main import TypeMixer as BaseTypeMixer, Generator as BaseGenerator
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

    def __init__(self, cls, generator=None):
        super(TypeMixer, self).__init__(cls, generator=generator)
        self.mapper = self.cls._sa_class_manager.mapper

    def get_value(self, column, fname, random=False, fake=False):
        if not isinstance(column, Column):
            import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
            return self.get_relation(column, fname)

        if not random and not fake:

            if column.default:
                return column.default.arg

            if column.nullable:
                return None

        return super(TypeMixer, self).get_value(column, fname, random, fake)

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

# lint_ignore=W0212
