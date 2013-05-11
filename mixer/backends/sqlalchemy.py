from __future__ import absolute_import
import datetime
import decimal

from ..main import TypeMixer as BaseTypeMixer, Generator as BaseGenerator
from ..generators import gen_small_integer
from sqlalchemy.types import (
    BIGINT, BOOLEAN, BigInteger, Boolean, CHAR, DATE, DATETIME, DECIMAL, Date,
    DateTime, FLOAT, Float, INT, INTEGER, Integer, NCHAR, NVARCHAR, NUMERIC,
    Numeric, SMALLINT, SmallInteger, String, TEXT, TIME, Text, Time, Unicode,
    UnicodeText, VARCHAR)


class Generator(BaseGenerator):
    types = {
        (String, VARCHAR, Unicode, NVARCHAR, NCHAR, CHAR, Text,
         UnicodeText, TEXT): str,
        (Boolean, BOOLEAN): str,
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

    def __load_fields(self):
        for column in self.cls._sa_class_manager.mapper.columns:
            yield column.name, column.type.__class__

# lint_ignore=W0212
