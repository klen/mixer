from __future__ import absolute_import

import datetime
from collections import defaultdict
import decimal
from ..main import (
    Field, Relation,
    TypeMixerMeta as BaseTypeMixerMeta,
    TypeMixer as BaseTypeMixer,
    Generator as BaseGenerator,
    Mixer as BaseMixer)
from .. import fakers as f
from .. import generators as g
from django.db import models


class Generator(BaseGenerator):
    types = {
        (models.CharField, models.TextField, models.SlugField): str,
        models.BooleanField: bool,
        models.BigIntegerField: long,
        (models.AutoField, models.IntegerField,
         models.PositiveIntegerField, models.SmallIntegerField): int,
        models.DateField: datetime.date,
        models.DateTimeField: datetime.datetime,
        models.TimeField: datetime.time,
        models.DecimalField: decimal.Decimal,
        models.FloatField: float,
    }


class TypeMixerMeta(BaseTypeMixerMeta):

    def __load_cls(cls, cls_type):
        if isinstance(cls_type, basestring):
            assert '.' in cls_type, ("'model_class' must be either a model"
                                     " or a model name in the format"
                                     " app_label.model_name")
            app_label, model_name = cls_type.split(".")
            cls_type = models.get_model(app_label, model_name)
        return cls_type


class TypeMixer(BaseTypeMixer):

    __metaclass__ = TypeMixerMeta

    generator = Generator

    def blend(self, **values):
        self.post_save_values = defaultdict(list)
        return super(TypeMixer, self).blend(**values)

    def set_value(self, target, field_name, field_value):

        field = self.fields.get(field_name)
        if field and field.scheme in self.cls._meta.local_many_to_many:
            if not isinstance(field_value, (list, tuple)):
                field_value = [field_value]
            self.post_save_values[field_name] += field_value
            return False

        return super(TypeMixer, self).set_value(
            target, field_name, field_value
        )

    def gen_field(self, target, field_name, field):
        if field.scheme.null and field.scheme.blank:
            return None

        if field.scheme.has_default():
            return self.set_value(
                target, field_name, field.scheme.get_default())

        if field.scheme.choices:
            choice = g.get_choice([c[0] for c in field.scheme.choices])
            return self.set_value(target, field_name, choice)

        super(TypeMixer, self).gen_field(target, field_name, field)

    def gen_select(self, target, field_name):
        field = self.fields.get(field_name)
        if field.is_relation:
            try:
                return field.scheme.model.objects.order_by('?')[0]
            except Exception:
                raise Exception(
                    "Cannot find a value for the field: '{0}'".format(
                        field_name
                    ))
        return super(TypeMixer, self).gen_select(target, field_name)

    def gen_random(self, target, field_name):
        field = self.fields.get(field_name)
        if field.is_relation:
            return self.gen_relation(target, field_name, field)
        return super(TypeMixer, self).gen_random(target, field_name)

    def gen_relation(self, target, field_name, relation):
        if relation.scheme.null or relation.scheme.blank:
            return None

        rel = relation.scheme
        new_scheme = rel.related.parent_model

        if new_scheme == self.cls:
            if relation.scheme in self.cls._meta.local_many_to_many:
                self.post_save_values[field_name] = [target]
            else:
                self.gen_select(target, field_name)
            return False

        value = self.mixer and self.mixer.blend(
            new_scheme, **relation.params
        ) or TypeMixer(
            new_scheme, mixer=self.mixer, generator=self.generator,
            fake=self.fake,
        ).blend(**relation.params)

        self.set_value(target, rel.name, value)

    def make_generator(self, field, fname=None, fake=False):
        fcls = type(field)
        stype = self.generator.cls_to_simple(fcls)
        gen_maker = self.generator.gen_maker(fcls, fname, fake)
        kwargs = dict()

        if stype is str:
            kwargs['length'] = field.max_length

        elif stype is decimal.Decimal:
            kwargs['i'] = field.max_digits - field.decimal_places
            kwargs['d'] = field.decimal_places

        if fcls is models.EmailField:
            return f.gen_email()

        if fcls is models.IPAddressField:
            return f.gen_ip4()

        if fcls is models.CommaSeparatedIntegerField:
            return g.gen_choices([1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
                                 field.max_length)

        return gen_maker(**kwargs)

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

    def post_generate(self, result, type_mixer):
        if self.commit:
            result.save()

        return result


# lint_ignore=W0212,W0201
