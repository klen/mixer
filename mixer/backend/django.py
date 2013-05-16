from __future__ import absolute_import

import datetime
import decimal
from ..main import (
    Relation, Field,
    TypeMixerMeta as BaseTypeMixerMeta,
    TypeMixer as BaseTypeMixer,
    Generator as BaseGenerator,
    Mixer as BaseMixer)
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

    def __load_cls(mcs, cls_type):
        if isinstance(cls_type, basestring):
            assert '.' in cls_type, ("'model_class' must be either a model"
                                     " or a model name in the format"
                                     " app_label.model_name")
            app_label, model_name = cls_type.split(".")
            cls_type = models.get_model(app_label, model_name)
        return cls_type


class TypeMixer(BaseTypeMixer):

    __metaclass__ = TypeMixerMeta


class Mixer(BaseMixer):

    type_mixer_cls = TypeMixer
