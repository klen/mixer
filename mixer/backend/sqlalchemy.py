from __future__ import absolute_import

import datetime

import decimal
from sqlalchemy import func
from sqlalchemy.orm.interfaces import MANYTOONE
from sqlalchemy.types import (
    BIGINT, BOOLEAN, BigInteger, Boolean, CHAR, DATE, DATETIME, DECIMAL, Date,
    DateTime, FLOAT, Float, INT, INTEGER, Integer, NCHAR, NVARCHAR, NUMERIC,
    Numeric, SMALLINT, SmallInteger, String, TEXT, TIME, Text, Time, Unicode,
    UnicodeText, VARCHAR)

from .. import mix_types as t
from ..main import (
    Relation, Field,
    TypeMixer as BaseTypeMixer,
    Generator as BaseGenerator,
    Mixer as BaseMixer)


class Generator(BaseGenerator):
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

    generator = Generator

    def __init__(self, cls, **params):
        """ Init TypeMixer and save the mapper.
        """
        super(TypeMixer, self).__init__(cls, **params)
        self.mapper = self.cls._sa_class_manager.mapper

    def gen_field(self, target, field_name, field):
        """
        Generate value by field.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param relation: Instance of :class:`Field`
        """
        column = field.scheme

        if (column.autoincrement and column.primary_key) \
                or column.nullable:
            return False

        if column.default:
            default = column.default.arg(target) \
                if column.default.is_callable \
                else column.default.arg
            return setattr(target, field_name, default)

        return super(TypeMixer, self).gen_value(target, field_name, column)

    def gen_random(self, target, field_name):
        """
        Generate random value of field with `field_name` for `target`

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        """
        field = self.fields.get(field_name)
        if isinstance(field, Relation):
            return self.gen_relation(target, field_name, field)
        return super(TypeMixer, self).gen_value(
            target, field_name, field.scheme, fake=False)

    def gen_select(self, target, field_name):
        """
        Select exists value from database.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        """
        if not self.mixer or not self.mixer.session:
            return False

        relation = self.mapper.get_property(field_name)
        value = self.mixer.session.query(
            relation.mapper.class_
        ).order_by(func.random()).first()
        setattr(target, field_name, value)

    def gen_relation(self, target, field_name, relation):
        """
        Generate a related relation by `relation`

        :param target: Target for generate value.
        :param field_name: Name of relation for generation.
        :param relation: Instance of :class:`Relation`

        """
        rel = relation.scheme
        if rel.direction == MANYTOONE:
            col = rel.local_remote_pairs[0][0]
            if col.nullable and not relation.params:
                return False

            value = self.mixer and self.mixer.blend(
                rel.mapper.class_,
                **relation.params
            ) or TypeMixer(
                rel.mapper.class_,
                mixer=self.mixer,
                generator=self.generator,
                fake=self.fake,
            ).blend(**relation.params)

            setattr(target, rel.key, value)
            setattr(target, col.name,
                    rel.mapper.identity_key_from_instance(value)[1][0])

    def make_generator(self, column, field_name=None, fake=False):
        """ Make values generator for column.

            :param column: SqlAlchemy column
            :param field_name: Field name
            :param fake: Force fake data
        """
        kwargs = dict()
        ftype = type(column.type)
        stype = self.generator.cls_to_simple(ftype)

        if stype is str:
            kwargs['length'] = column.type.length

        return self.generator.gen_maker(stype, field_name, fake)(**kwargs)

    def __load_fields(self):
        """ Prepare SQLALchemyTypeMixer.
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
        """Initialize the SQLAlchemy Mixer.

        :param fake: (True) Generate fake data instead of random data.
        :param session: SQLAlchemy session. Using for commits.
        :param commit: (False) Commit instance to session after creation.

        """
        super(Mixer, self).__init__(**params)
        self.session = session
        assert not commit or self.session, "Set session for commits"
        self.commit = commit

    def post_generate(self, result, type_mixer):
        if self.commit:
            self.session.add(result)
            self.session.commit()

        return result

# lint_ignore=W0212
