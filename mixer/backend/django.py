from __future__ import absolute_import

import datetime
import decimal

from django.db import models

from .. import generators as g, mix_types as t, six
from ..main import (
    Field, Relation,
    TypeMixerMeta as BaseTypeMixerMeta,
    TypeMixer as BaseTypeMixer,
    Generator as BaseGenerator,
    Mixer as BaseMixer)


class Generator(BaseGenerator):
    types = {
        (models.CharField, models.SlugField): str,
        models.TextField: t.Text,
        models.BooleanField: bool,
        models.BigIntegerField: t.BigInteger,
        (models.AutoField, models.IntegerField): int,
        models.PositiveIntegerField: t.PositiveInteger,
        models.PositiveSmallIntegerField: t.PositiveSmallInteger,
        models.SmallIntegerField: t.SmallInteger,
        models.DateField: datetime.date,
        models.DateTimeField: datetime.datetime,
        models.TimeField: datetime.time,
        models.DecimalField: decimal.Decimal,
        models.FloatField: float,
        models.EmailField: t.EmailString,
        models.IPAddressField: t.IP4String,
    }


class TypeMixerMeta(BaseTypeMixerMeta):

    def __load_cls(cls, cls_type):
        if isinstance(cls_type, six.string_types):
            assert '.' in cls_type, ("'model_class' must be either a model"
                                     " or a model name in the format"
                                     " app_label.model_name")
            app_label, model_name = cls_type.split(".")
            cls_type = models.get_model(app_label, model_name)
        return cls_type


class TypeMixer(six.with_metaclass(TypeMixerMeta, BaseTypeMixer)):

    __metaclass__ = TypeMixerMeta

    generator = Generator

    def set_value(self, target, field_name, field_value, finaly=False):

        field = self.fields.get(field_name)
        if field and field.scheme in self.cls._meta.local_many_to_many:
            if not isinstance(field_value, (list, tuple)):
                field_value = [field_value]
            return field_name, field_value

        return super(TypeMixer, self).set_value(
            target, field_name, field_value, finaly
        )

    def gen_field(self, target, field_name, field):
        if field.scheme.null and field.scheme.blank:
            return None

        if field.scheme.has_default():
            return self.set_value(
                target, field_name, field.scheme.get_default())

        super(TypeMixer, self).gen_field(target, field_name, field)

    def gen_select(self, target, field_name):
        field = self.fields.get(field_name)
        if field:
            try:
                return self.set_value(
                    target, field_name,
                    field.scheme.rel.to.objects.order_by('?')[0]
                )
            except Exception:
                raise Exception(
                    "Cannot find a value for the field: '{0}'".format(
                        field_name
                    ))
        return super(TypeMixer, self).gen_select(target, field_name)

    def gen_random(self, target, field_name):
        field = self.fields.get(field_name)
        if field and field.is_relation:
            return self.gen_relation(target, field_name, field, force=True)
        return super(TypeMixer, self).gen_random(target, field_name)

    def gen_relation(self, target, field_name, relation, force=False):
        if (
                not relation.scheme
                or relation.scheme.null
                or relation.scheme.blank
                or relation.scheme.auto_created
        ) and not relation.params and not force:
            return None

        rel = relation.scheme
        if not rel:
            raise ValueError('Unknown relation: %s' % field_name)

        new_scheme = rel.related.parent_model

        value = target
        if new_scheme != self.cls:
            value = self.mixer and self.mixer.blend(
                new_scheme, **relation.params
            ) or TypeMixer(
                new_scheme, mixer=self.mixer, generator=self.generator,
                fake=self.fake,
            ).blend(**relation.params)

        return self.set_value(target, rel.name, value)

    def make_generator(self, field, fname=None, fake=False):
        fcls = type(field)
        stype = self.generator.cls_to_simple(fcls)

        kwargs = dict()

        if fcls is models.CommaSeparatedIntegerField:
            return g.gen_choices(
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], field.max_length)

        if field and field.choices:
            choices, _ = list(zip(*field.choices))
            return g.gen_choice(choices)

        if stype is str:
            kwargs['length'] = field.max_length

        elif stype is decimal.Decimal:
            kwargs['i'] = field.max_digits - field.decimal_places
            kwargs['d'] = field.decimal_places

        gen_maker = self.generator.gen_maker(fcls, fname, fake)
        return gen_maker(**kwargs)

    @staticmethod
    def is_unique(field):
        return field.scheme.unique

    def __load_fields(self):
        for field in self.cls._meta.fields:

            if isinstance(field, models.AutoField)\
                    and self.mixer and self.mixer.commit:
                continue

            if isinstance(field, models.ForeignKey):
                yield field.name, Relation(field, field.name)
                continue

            yield field.name, Field(field, field.name)

        for field in self.cls._meta.local_many_to_many:
            yield field.name, Relation(field, field.name)


class Mixer(BaseMixer):

    type_mixer_cls = TypeMixer

    def __init__(self, commit=True, **params):
        super(Mixer, self).__init__(**params)
        self.commit = commit

    def post_generate(self, result):
        if self.commit:
            result.save()

        return result


# Default mixer
mixer = Mixer()

# lint_ignore=W0212,W0201,E1002,F0401
