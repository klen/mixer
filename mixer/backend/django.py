""" Django support. """
from __future__ import absolute_import

import datetime
import decimal
from os import path

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django import VERSION
from django.core.files.base import ContentFile

from .. import generators as g, mix_types as t
from .. import _compat as _
from ..main import (
    SKIP_VALUE, TypeMixerMeta as BaseTypeMixerMeta, TypeMixer as BaseTypeMixer,
    GenFactory as BaseFactory, Mixer as BaseMixer, _Deffered)


get_contentfile = ContentFile

if VERSION < (1, 4):
    get_contentfile = lambda content, name: ContentFile(content)


MOCK_FILE = path.abspath(path.join(
    path.dirname(path.dirname(__file__)), 'resources', 'file.txt'
))
MOCK_IMAGE = path.abspath(path.join(
    path.dirname(path.dirname(__file__)), 'resources', 'image.jpg'
))


def get_file(filepath=MOCK_FILE, **kwargs):
    """ Generate a content file.

    :return ContentFile:

    """
    with open(filepath, 'rb') as f:
        name = path.basename(filepath)
        return get_contentfile(f.read(), name)


def get_image(filepath=MOCK_IMAGE):
    """ Generate a content image.

    :return ContentFile:

    """
    return get_file(filepath)


def get_relation(_pylama_scheme=None, _pylama_typemixer=None, **params):
    """ Function description. """
    scheme = _pylama_scheme.related.parent_model

    if scheme is ContentType:
        choices = [m for m in models.get_models() if m is not ContentType]
        return ContentType.objects.get_for_model(g.get_choice(choices))

    return TypeMixer(
        scheme,
        mixer=_pylama_typemixer._TypeMixer__mixer,
        factory=_pylama_typemixer._TypeMixer__factory,
        fake=_pylama_typemixer._TypeMixer__fake,
    ).blend(**params)


class GenFactory(BaseFactory):

    """ Map a django classes to simple types. """

    types = {
        (models.AutoField, models.IntegerField): int,
        (models.CharField, models.SlugField): str,
        models.BigIntegerField: t.BigInteger,
        models.BooleanField: bool,
        models.DateField: datetime.date,
        models.DateTimeField: datetime.datetime,
        models.DecimalField: decimal.Decimal,
        models.EmailField: t.EmailString,
        models.FloatField: float,
        models.IPAddressField: t.IP4String,
        models.PositiveIntegerField: t.PositiveInteger,
        models.PositiveSmallIntegerField: t.PositiveSmallInteger,
        models.SmallIntegerField: t.SmallInteger,
        models.TextField: t.Text,
        models.TimeField: datetime.time,
        models.URLField: t.URL,
    }

    generators = {
        models.FileField: get_file,
        models.ImageField: get_image,
        models.ForeignKey: get_relation,
        models.ManyToManyField: get_relation,
    }


class TypeMixerMeta(BaseTypeMixerMeta):

    """ Load django models from strings. """

    def __new__(mcs, name, bases, params):
        """ Associate Scheme with Django models.

        Cache Django models.

        :return mixer.backend.django.TypeMixer: A generated class.

        """
        params['models_cache'] = dict()
        cls = super(TypeMixerMeta, mcs).__new__(mcs, name, bases, params)
        cls.__update_cache()
        return cls

    def __load_cls(cls, cls_type):

        if isinstance(cls_type, _.string_types):
            if '.' in cls_type:
                app_label, model_name = cls_type.split(".")
                return models.get_model(app_label, model_name)

            else:
                try:
                    if cls_type not in cls.models_cache:
                        cls.__update_cache()

                    return cls.models_cache[cls_type]
                except KeyError:
                    raise ValueError('Model "%s" not found.' % cls_type)

        return cls_type

    def __update_cache(cls):
        for app_models in models.loading.cache.app_models.values():
            for name, model in app_models.items():
                cls.models_cache[name] = model


class TypeMixer(_.with_metaclass(TypeMixerMeta, BaseTypeMixer)):

    """ TypeMixer for Django. """

    __metaclass__ = TypeMixerMeta

    factory = GenFactory

    def get_value(self, field_name, field_value):
        """ Set value to generated instance.

        :return : None or (name, value) for later use

        """
        field = self.__fields.get(field_name)

        if field and (field.scheme in self.__scheme._meta.local_many_to_many or
                      type(field.scheme) is GenericForeignKey):
            return field_name, _Deffered(field_value, field.scheme)

        return super(TypeMixer, self).get_value(field_name, field_value)

    @staticmethod
    def get_default(field):
        """ Get default value from field.

        :return value: A default value or SKIP_VALUE

        """
        if not field.scheme.has_default():
            return SKIP_VALUE

        return field.scheme.get_default()

    def gen_select(self, field_name, select):
        """ Select exists value from database.

        :param field_name: Name of field for generation.

        :return : None or (name, value) for later use

        """
        field = self.__fields.get(field_name)
        if not field:
            return super(TypeMixer, self).gen_select(field_name, select)

        try:
            return field.name, field.scheme.rel.to.objects.filter(
                **select.params).order_by('?')[0]

        except Exception:
            raise Exception(
                "Cannot find a value for the field: '{0}'".format(field_name))

    def gen_field(self, field):
        """ Generate value by field.

        :param relation: Instance of :class:`Field`

        :return : None or (name, value) for later use

        """
        if isinstance(field.scheme, GenericForeignKey):
            return field.name, SKIP_VALUE

        if field.params and not field.scheme:
            raise ValueError('Invalid relation %s' % field.name)

        return super(TypeMixer, self).gen_field(field)

    def make_generator(self, field, fname=None, fake=False, args=None, kwargs=None): # noqa
        """ Make values generator for field.

        :param field: A mixer field
        :param field_name: Field name
        :param fake: Force fake data

        :return generator:

        """
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs

        fcls = type(field)
        stype = self.__factory.cls_to_simple(fcls)

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

        elif isinstance(field, models.fields.related.RelatedField):
            kwargs.update({'_pylama_typemixer': self, '_pylama_scheme': field})

        return super(TypeMixer, self).make_generator(
            fcls, field_name=fname, fake=fake, args=[], kwargs=kwargs)

    @staticmethod
    def is_unique(field):
        """ Return True is field's value should be a unique.

        :return bool:

        """
        return field.scheme.unique

    @staticmethod
    def is_required(field):
        """ Return True is field's value should be defined.

        :return bool:

        """
        if field.params:
            return True

        if field.scheme.null and field.scheme.blank:
            return False

        if field.scheme.auto_created:
            return False

        if isinstance(field.scheme, models.ManyToManyField):
            return False

        return True

    def guard(self, **filters):
        """ Look objects in database.

        :returns: A finded object or False

        """
        qs = self.__scheme.objects.filter(**filters)
        count = qs.count()

        if count == 1:
            return qs.get()

        if count:
            return list(qs)

        return False

    def __load_fields(self):

        for field in self.__scheme._meta.virtual_fields:
            yield field.name, t.Field(field, field.name)

        for field in self.__scheme._meta.fields:

            if isinstance(field, models.AutoField)\
                    and self.__mixer and self.__mixer.params.get('commit'):
                continue

            if isinstance(field, models.ForeignKey):
                yield field.name, t.Field(field, field.name)
                continue

            yield field.name, t.Field(field, field.name)

        for field in self.__scheme._meta.local_many_to_many:
            yield field.name, t.Field(field, field.name)


class Mixer(BaseMixer):

    """ Integration with Django. """

    type_mixer_cls = TypeMixer

    def __init__(self, commit=True, **params):
        """Initialize Mixer instance.

        :param commit: (True) Save object to database.

        """
        super(Mixer, self).__init__(**params)
        self.params['commit'] = commit

    def postprocess(self, target, postprocess_values):
        """ Save objects in db.

        :return value: A generated value

        """
        if self.params.get('commit'):
            target.save()

        for name, deffered in postprocess_values:

            value = deffered.value

            if not type(deffered.scheme) is GenericForeignKey:

                # # If the ManyToMany relation has an intermediary model,
                # # the add and remove methods do not exist.
                if not deffered.scheme.rel.through._meta.auto_created:
                    self.blend(
                        deffered.scheme.rel.through, **{
                            deffered.scheme.m2m_field_name(): target,
                            deffered.scheme.m2m_reverse_field_name(): value})
                    continue

                if not isinstance(value, (list, tuple)):
                    value = [value]

            setattr(target, name, value)

        return target


# Default mixer
mixer = Mixer()
