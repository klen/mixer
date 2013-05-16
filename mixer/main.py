import datetime

import decimal
from importlib import import_module

from . import generators as g, fakers as f


DEFAULT = object()
RANDOM = object()
FAKE = object()
SELECT = object()


class Field(object):
    """ Store field imformation.
    """
    def __init__(self, scheme, name):
        self.scheme = scheme
        self.name = name


class Relation(Field):
    """ Store relation field imformation.
    """
    def __init__(self, scheme, name, params=None):
        super(Relation, self).__init__(scheme, name)
        self.params = params or dict()


class GeneratorMeta(type):
    """ Precache generators.
    """
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
    """ Make generators for types.
    """
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
    """ Cache mixers by class.
    """
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

    fake = FAKE
    generator = Generator
    select = SELECT
    random = RANDOM

    def __init__(self, cls, mixer=None, generator=None):
        self.cls = cls
        self.mixer = mixer
        self.fields = dict(self.__load_fields())
        self.generator = generator or self.generator
        self.generators = dict()

    def __repr__(self):
        return "<TypeMixer {0}>".format(self.cls)

    def blend(self, **values):
        target = self.cls()

        defaults = dict(**self.fields)

        # Prepare relations
        for key, params in values.items():
            if '__' in key:
                rname, rvalue = key.split('__', 1)
                field = defaults.get(rname)
                defaults.setdefault(rname, Relation(field.scheme, field.name))
                defaults[rname].params.update({rvalue: params})
                del values[key]

        defaults.update(values)

        for fname, fvalue in defaults.items():
            if isinstance(fvalue, Relation):
                self.gen_relation(target, fname, fvalue)

            elif isinstance(fvalue, Field):
                self.gen_field(target, fname, fvalue)

            elif fvalue is self.random:
                self.gen_random(target, fname)

            elif fvalue is self.fake:
                self.gen_fake(target, fname)

            elif fvalue is self.select:
                self.gen_select(target, fname)

            else:
                self.set_value(target, fname, fvalue)

        return target

    @staticmethod
    def set_value(target, fname, fvalue):
        if callable(fvalue):
            fvalue = fvalue()
        setattr(target, fname, fvalue)

    def gen_value(self, target, fname, fcls, fake=False):
        """ Generate values from basic types.
            Set value to target.
        """
        gen = self.get_generator(fcls, fname, fake=fake)
        setattr(target, fname, next(gen))

    def gen_field(self, target, fname, field):
        """ Generate value by field scheme.
        """
        self.gen_value(target, fname, field.scheme)

    def gen_relation(self, target, fname, relation):
        """ Blend a relation object.
        """
        mixer = TypeMixer(relation.scheme, self.mixer, self.generator)
        setattr(target, fname, mixer.blend(**relation.params))

    def gen_random(self, target, fname):
        field = self.fields.get(fname)
        self.gen_value(target, fname, field.scheme)

    gen_select = gen_random

    def gen_fake(self, target, fname):
        field = self.fields.get(fname)
        self.gen_value(target, fname, field.scheme, fake=True)

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
            yield fname, Field(getattr(self.cls, fname), fname)


class Mixer(object):

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
