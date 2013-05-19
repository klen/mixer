from __future__ import absolute_import

import datetime
import decimal
from ..main import (
    Field, Relation,
    TypeMixerMeta as BaseTypeMixerMeta,
    TypeMixer as BaseTypeMixer,
    Generator as BaseGenerator,
    Mixer as BaseMixer)
from .. import fakers as f
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

    def gen_relation(self, target, field_name, relation):
        rel = relation.scheme
        value = self.mixer and self.mixer.blend(
            rel.related.parent_model, **relation.params
        ) or TypeMixer(
            rel.related.parent_model,
            mixer=self.mixer,
            generator=self.generator,
            fake=self.fake,
        ).blend(**relation.params)
        setattr(target, rel.name, value)

    def make_generator(self, field, fname=None, fake=False):
        fcls = type(field)
        stype = self.generator.cls_to_simple(fcls)
        gen_maker = self.generator.gen_maker(fcls, fname, fake)
        kwargs = dict()

        if stype is str:
            kwargs['length'] = field.max_length

        if fcls is models.EmailField:
            return f.gen_email()

        if fcls is models.IPAddressField:
            return f.gen_ip4()

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


class Mixer(BaseMixer):

    type_mixer_cls = TypeMixer

    def __init__(self, commit=False, **params):
        super(Mixer, self).__init__(**params)
        self.commit = commit

    def blend(self, scheme, **values):
        result = super(Mixer, self).blend(scheme, **values)

        if self.commit:
            result.save()

        return result


# lint_ignore=W0212
