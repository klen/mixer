from __future__ import absolute_import

import datetime

import decimal
from sqlalchemy import func
from sqlalchemy.orm.interfaces import MANYTOONE
# from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.types import (
    BIGINT, BOOLEAN, BigInteger, Boolean, CHAR, DATE, DATETIME, DECIMAL, Date,
    DateTime, FLOAT, Float, INT, INTEGER, Integer, NCHAR, NVARCHAR, NUMERIC,
    Numeric, SMALLINT, SmallInteger, String, TEXT, TIME, Text, Time, Unicode,
    UnicodeText, VARCHAR)

from ..generators import gen_small_integer
from ..main import (
    Relation, Field,
    TypeMixer as BaseTypeMixer,
    Generator as BaseGenerator,
    Mixer as BaseMixer)


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
        """ Init TypeMixer and save the mapper.
        """
        super(TypeMixer, self).__init__(cls, **params)
        self.mapper = self.cls._sa_class_manager.mapper

    # def set_value(self, target, fname, fvalue):
        # super(TypeMixer, self).set_value(target, fname, fvalue)
        # field = self.fields.get(fname)
        # if isinstance(field.scheme, RelationshipProperty)\
                # and field.scheme.direction == MANYTOONE:
            # relation = field.scheme
            # col = relation.local_remote_pairs[0][0]
            # import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
            # setattr(target, col.name,
                # relation.mapper.identity_key_from_instance(fvalue)[1][0])

    def gen_field(self, target, fname, field):
        column = field.scheme

        if (column.autoincrement and column.primary_key) \
                or column.nullable:
            return False

        if column.default:
            default = column.default.arg(target) \
                if column.default.is_callable \
                else column.default.arg
            return setattr(target, fname, default)

        return super(TypeMixer, self).gen_value(target, fname, column)

    def gen_random(self, target, fname):
        field = self.fields.get(fname)
        return super(TypeMixer, self).gen_value(target, fname, field.scheme)

    def gen_select(self, target, fname):
        if not self.mixer or not self.mixer.session:
            return False

        relation = self.mapper.get_property(fname)
        value = self.mixer.session.query(
            relation.mapper.class_
        ).order_by(func.random()).first()
        setattr(target, fname, value)

    def gen_relation(self, target, fname, field):
        relation = field.scheme
        if relation.direction == MANYTOONE:
            relname = relation.back_populates
            if relname and relation.mapper.get_property(relname):
                field.params[relname] = target

        col = relation.local_remote_pairs[0][0]
        if col.nullable and not field.params:
            return None

        mixer = TypeMixer(relation.mapper.class_)
        value = mixer.blend(**field.params)
        setattr(target, fname, value)
        # setattr(target, col.name,
                # relation.mapper.identity_key_from_instance(value)[1][0])

    def gen_fake(self, target, fname):
        field = self.fields.get(fname)
        return super(TypeMixer, self).gen_value(
            target, fname, field.scheme, fake=True)

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
            yield rel.key, Relation(rel, rel.key)

        for column in mapper.columns:
            if not column in relations:
                yield column.name, Field(column, column.name)


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
