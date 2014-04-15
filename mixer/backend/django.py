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
    NO_VALUE, TypeMixerMeta as BaseTypeMixerMeta, TypeMixer as BaseTypeMixer,
    GenFactory as BaseFactory, Mixer as BaseMixer)


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


def get_contenttype(**kwargs):
    """ Generate a content type value.

    :return ContentType:

    """
    choices = [m for m in models.get_models() if m is not ContentType]
    return ContentType.objects.get_for_model(g.get_choice(choices))


def get_relation(_pylama_scheme=None, _pylama_typemixer=None, **params):
    """ Function description. """
    scheme = _pylama_scheme.related.parent_model
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
        ContentType: get_contenttype,
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

    def set_value(self, target, field_name, field_value, finaly=False):
        """ Set value to generated instance.

        :return : None or (name, value) for later use

        """
        field = self.__fields.get(field_name)
        if field and field.scheme in self.__scheme._meta.local_many_to_many:

            if not target.pk:
                return field_name, field_value

            # If the ManyToMany relation has an intermediary model,
            # the add and remove methods do not exist.
            if not field.scheme.rel.through._meta.auto_created:
                return self.__mixer.blend(
                    field.scheme.rel.through,
                    **{
                        field.scheme.m2m_field_name(): target,
                        field.scheme.m2m_reverse_field_name(): field_value,
                    }
                )
            if not isinstance(field_value, (list, tuple)):
                field_value = [field_value]

            setattr(target, field_name, field_value)

            return True

        return super(TypeMixer, self).set_value(
            target, field_name, field_value, finaly)

    @staticmethod
    def get_default(field, target):
        """ Get default value from field.

        :return value: A default value or NO_VALUE

        """
        if not field.scheme.has_default():
            return NO_VALUE

        return field.scheme.get_default()

    def gen_select(self, target, field_name, select):
        """ Select exists value from database.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.

        :return : None or (name, value) for later use

        """
        field = self.__fields.get(field_name)
        if not field:
            return super(TypeMixer, self).gen_select(
                target, field_name, select)

        try:
            return self.set_value(
                target, field_name, field.scheme.rel.to.objects
                .filter(**select.params).order_by('?')[0])

        except Exception:
            raise Exception(
                "Cannot find a value for the field: '{0}'".format(field_name))

    def gen_relation(self, target, relation, force=False):
        """ Generate a related relation by `relation`.

        :param target: Target for generate value.
        :param relation: Instance of :class:`Relation`

        :return : None or (name, value) for later use

        """
        if isinstance(relation.scheme, GenericForeignKey):
            return None

        if (
                not relation.scheme
                or relation.scheme.null
                or relation.scheme.blank
                or relation.scheme.auto_created
        ) and not relation.params and not force:
            return None

        rel = relation.scheme
        if not rel:
            raise ValueError('Unknown relation: %s' % relation.name)

        if isinstance(rel, models.ForeignKey) and rel.value_from_object(target): # noqa
            return None

        new_scheme = rel.related.parent_model

        value = target
        if new_scheme != self.__scheme:
            value = self.__mixer and self.__mixer.blend(
                new_scheme, **relation.params
            ) or TypeMixer(
                new_scheme, factory=self.__factory, fake=self.fake,
            ).blend(**relation.params)

        return self.set_value(target, rel.name, value)

    def gen_field(self, target, field):
        """ Generate value by field.

        :param target: Target for generate value.
        :param relation: Instance of :class:`Field`

        :return : None or (name, value) for later use

        """
        if isinstance(field.scheme, GenericForeignKey):
            return None

        if field.params and not field.scheme:
            raise ValueError('Invalid relation %s' % field.name)

        if not isinstance(field.scheme, models.ManyToManyField) and field.scheme.value_from_object(target): # noqa
            return None

        return super(TypeMixer, self).gen_field(target, field)

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

    def post_generate(self, result):
        """ Save objects in db.

        :return value: A generated value

        """
        if self.params.get('commit'):
            result.save()

        return result


# Default mixer
mixer = Mixer()
