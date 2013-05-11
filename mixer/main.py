import datetime

import decimal
from importlib import import_module

from . import generators as g, fakers as f


RANDOM = object()
FAKE = object()


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


class TypeMixer(object):

    random = RANDOM
    fake = FAKE
    generator = Generator

    def __init__(self, cls, generator=None):
        self.cls = self.__load_cls(cls)
        self.fields = list(self.__load_fields())
        self.generator = generator or self.generator
        self.generators = dict()

    def blend(self, **values):
        target = self.cls()
        for fname, fcls in self.fields:
            value = values.get(fname, self.random)

            if value is self.random:
                value = self.get_random(fcls)

            if value is self.fake:
                value = self.get_fake(fcls, fname)

            setattr(target, fname, value)

        return target

    def get_random(self, fcls):
        gen = self.get_generator(fcls)
        return next(gen)

    def get_fake(self, fcls, fname):
        gen = self.get_generator(fcls, fname, True)
        return next(gen)

    def get_generator(self, fcls, fname=None, fake=False):
        key = fcls, fname, fake
        if not key in self.generators:
            gen_maker = self.generator.gen_maker(*key)
            self.generators[key] = gen_maker()
        return self.generators[key]

    @staticmethod
    def __load_cls(cls_type):
        if isinstance(cls_type, basestring):
            mod, cls_type = cls_type.rsplit('.', 1)
            mod = import_module(mod)
            cls_type = getattr(mod, cls_type)
        return cls_type

    def __load_fields(self):
        for fname in dir(self.cls):
            if fname.startswith('_'):
                continue
            yield fname, getattr(self.cls, fname)
