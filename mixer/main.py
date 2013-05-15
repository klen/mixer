import datetime

import decimal
from importlib import import_module
from collections import defaultdict

from . import generators as g, fakers as f


DEFAULT = object()
RANDOM = object()
FAKE = object()
SELECT = object()


class GeneratorMeta(type):

    def __new__(mcs, name, bases, params):
        generators = dict()
        fakers = dict()
        types = dict()

        for cls in bases:
            if isinstance(cls, GeneratorMeta):
                generators.update(cls.generators)
                fakers.update(cls.fakers)
                types.update(cls.types)

        generators.update(params.get('generators', dict()))
        fakers.update(params.get('fakers', dict()))
        types.update(params.get('types', dict()))

        mcs.flat_keys(generators)
        mcs.flat_keys(types)

        params['generators'] = generators
        params['fakers'] = fakers
        params['types'] = types

        return super(GeneratorMeta, mcs).__new__(mcs, name, bases, params)

    @staticmethod
    def flat_keys(d):
        for key, value in d.items():
            if isinstance(key, (tuple, list)):
                for k in key:
                    d[k] = value
                del d[key]
        return d


class Generator(object):

    __metaclass__ = GeneratorMeta

    generators = {
        bool: g.gen_boolean,
        float: g.gen_float,
        int: g.gen_integer,
        long: g.gen_big_integer,
        str: g.gen_string,
        datetime.datetime: g.gen_datetime,
        datetime.time: g.gen_time,
        decimal.Decimal: g.gen_decimal,
        None: g.loop(lambda: ''),
    }

    fakers = {
        ('name', str): f.gen_name,
        ('description', str): f.gen_lorem,
        ('content', str): f.gen_lorem,
        ('city', str): f.gen_city,
    }

    types = {
        unicode: str,
    }

    @classmethod
    def cls_to_simple(cls, fcls):
        """ Translate class to one of simple base types.
        """
        return cls.types.get(fcls) or (
            fcls if fcls in cls.generators
            else None
        )

    @staticmethod
    def name_to_simple(fname):
        """ Translate name to one of simple base names.
        """
        fname = fname or ''
        return fname.lower().strip()

    @classmethod
    def gen_maker(cls, fcls, fname=None, fake=False):
        """ Generate value based on class and name.
        """
        fcls = cls.cls_to_simple(fcls)
        fname = cls.name_to_simple(fname)

        gen_maker = cls.generators.get(fcls)

        if fname and fake and (fname, fcls) in cls.fakers:
            gen_maker = cls.fakers.get((fname, fcls)) or gen_maker

        return gen_maker


class TypeMixerMeta(type):
    mixers = dict()

    def __call__(cls, cls_type, mixer=None, generator=None):
        cls_type = cls.__load_cls(cls_type)
        key = (mixer, cls_type)
        if not key in cls.mixers:
            cls.mixers[key] = super(TypeMixerMeta, cls).__call__(
                cls_type, mixer=mixer, generator=generator
            )
        return cls.mixers[key]

    @staticmethod
    def __load_cls(cls_type):
        if isinstance(cls_type, basestring):
            mod, cls_type = cls_type.rsplit('.', 1)
            mod = import_module(mod)
            cls_type = getattr(mod, cls_type)
        return cls_type


class TypeMixer(object):

    __metaclass__ = TypeMixerMeta

    default = DEFAULT
    fake = FAKE
    generator = Generator
    select = SELECT
    random = RANDOM

    def __init__(self, cls, mixer=None, generator=None):
        self.cls = cls
        self.mixer = mixer
        self.fields = list(self.__load_fields())
        self.generator = generator or self.generator
        self.generators = dict()

    def blend(self, **values):
        target = self.cls()

        # Prepare relations
        relations = defaultdict(defaultdict)
        for key, params in values.items():
            if '__' in key:
                rname, rvalue = key.split('__', 1)
                relations[rname][rvalue] = params
                del values[key]

        # Fill fields
        for fname, fcls in self.fields:

            if fname in relations:
                params = relations[fname]
                self.set_relation(target, fcls, fname, params=params)
                continue

            value = values.get(fname, self.default)

            if value in [self.default, self.random, self.fake, self.select]:
                self.set_value(
                    target, fcls, fname,
                    random=value is self.random,
                    fake=value is self.fake,
                    select=value is self.select,
                )
                continue

            setattr(target, fname, value)

        return target

    @staticmethod
    def set_relation(target, fcls, fname, random=False, fake=False,
                     select=False, params=None):
        params = params or dict()
        mixer = TypeMixer(fcls)
        setattr(target, fname, mixer.blend(**params))

    def set_value(self, target, fcls, fname, random=False, fake=False,
                  select=False):
        gen = self.get_generator(fcls, fname, fake)
        setattr(target, fname, next(gen))

    def get_generator(self, fcls, fname=None, fake=False):
        key = fcls, fname, fake
        if not key in self.generators:
            self.generators[key] = self.make_generator(fcls, fname, fake)
        return self.generators[key]

    def make_generator(self, fcls, fname=None, fake=False):
        return self.generator.gen_maker(fcls, fname, fake)()

    def __load_fields(self):
        for fname in dir(self.cls):
            if fname.startswith('_'):
                continue
            yield fname, getattr(self.cls, fname)


class Mixer(object):

    default = DEFAULT
    fake = FAKE
    select = SELECT
    random = RANDOM
    type_mixer_cls = TypeMixer

    def __init__(self, fake=False, **params):
        self.params = params
        self.fake = fake

    def blend(self, cls_type, **values):
        type_mixer = self.type_mixer_cls(cls_type, mixer=self)
        return type_mixer.blend(**values)
