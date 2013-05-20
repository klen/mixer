from __future__ import absolute_import

import datetime
from copy import deepcopy

import decimal
from importlib import import_module
from collections import defaultdict
from types import GeneratorType

from . import generators as g, fakers as f, mix_types as t
from . import six


DEFAULT = object()
RANDOM = object()
FAKE = object()
SELECT = object()


class Field(object):
    """ Store field imformation.
    """
    is_relation = False

    def __init__(self, scheme, name):
        self.scheme = scheme
        self.name = name

    def __deepcopy__(self, memo):
        return Field(self.scheme, self.name)


class Relation(Field):
    """ Store relation field imformation.
    """
    is_relation = True

    def __init__(self, scheme, name, params=None):
        super(Relation, self).__init__(scheme, name)
        self.params = params or dict()

    def __deepcopy__(self, memo):
        return Relation(self.scheme, self.name, deepcopy(self.params))


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

        generators = dict(mcs.flat_keys(generators))
        types = dict(mcs.flat_keys(types))

        params['generators'] = generators
        params['fakers'] = fakers
        params['types'] = types

        return super(GeneratorMeta, mcs).__new__(mcs, name, bases, params)

    @staticmethod
    def flat_keys(d):
        for key, value in d.items():
            if isinstance(key, (tuple, list)):
                for k in key:
                    yield k, value
                continue
            yield key, value


class Generator(six.with_metaclass(GeneratorMeta)):
    """ Make generators for types.
    """
    generators = {
        bool: g.gen_boolean,
        float: g.gen_float,
        int: g.gen_integer,
        str: g.gen_string,
        datetime.date: g.gen_date,
        datetime.datetime: g.gen_datetime,
        datetime.time: g.gen_time,
        decimal.Decimal: g.gen_decimal,
        t.BigInteger: g.gen_big_integer,
        t.EmailString: f.gen_email,
        t.HostnameString: f.gen_hostname,
        t.IP4String: f.gen_ip4,
        t.NullOrBoolean: g.gen_null_or_boolean,
        t.PositiveDecimal: g.gen_positive_decimal,
        t.PositiveInteger: g.gen_positive_integer,
        t.SmallInteger: g.gen_small_integer,
        t.Text: f.gen_lorem,
        None: g.loop(lambda: ''),
    }

    fakers = {
        ('name', str): f.gen_name,
        ('first_name', str): f.gen_firstname,
        ('firstname', str): f.gen_firstname,
        ('last_name', str): f.gen_lastname,
        ('lastname', str): f.gen_lastname,
        ('title', str): f.gen_lorem,
        ('description', str): f.gen_lorem,
        ('content', str): f.gen_lorem,
        ('city', str): f.gen_city,
        ('country', str): f.gen_country,
        ('email', str): f.gen_email,
        ('username', str): f.gen_username,
        ('login', str): f.gen_username,
    }

    types = {}

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

    def __call__(cls, cls_type, mixer=None, generator=None, fake=True):
        cls_type = cls.__load_cls(cls_type)
        key = (mixer, cls_type)
        if not key in cls.mixers:
            cls.mixers[key] = super(TypeMixerMeta, cls).__call__(
                cls_type, mixer=mixer, generator=generator, fake=fake,
            )
        return cls.mixers[key]

    @staticmethod
    def __load_cls(cls_type):
        if isinstance(cls_type, six.string_types):
            mod, cls_type = cls_type.rsplit('.', 1)
            mod = import_module(mod)
            cls_type = getattr(mod, cls_type)
        return cls_type


class TypeMixer(six.with_metaclass(TypeMixerMeta)):

    fake = FAKE
    generator = Generator
    select = SELECT
    random = RANDOM

    def __init__(self, cls, mixer=None, generator=None, fake=True):
        self.cls = cls
        self.mixer = mixer
        self.fake = fake

        if self.mixer:
            self.fake = self.mixer.fake

        self.fields = dict(self.__load_fields())
        self.generator = generator or self.generator
        self.generators = dict()
        self.post_save_values = defaultdict(list)

    def __repr__(self):
        return "<TypeMixer {0}>".format(self.cls)

    def blend(self, **values):
        """
        Generate instance.

        :param **values: Predefined fields
        """
        target = self.cls()
        self.post_save_values = defaultdict(list)

        defaults = deepcopy(self.fields)

        # Prepare relations
        for key, params in values.items():
            if '__' in key:
                rname, rvalue = key.split('__', 1)
                field = defaults.get(rname)
                if not isinstance(field, Relation):
                    defaults[rname] = Relation(field.scheme, field.name)
                defaults[rname].params.update({rvalue: params})
                continue
            defaults[key] = params

        # Fill fields
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
    def set_value(target, field_name, field_value):
        """ Set `value` to `target` as `field_name`.
        """
        if callable(field_value):
            field_value = field_value()

        elif isinstance(field_value, GeneratorType):
            field_value = next(field_value)

        setattr(target, field_name, field_value)

    def gen_value(self, target, fname, fcls, fake=None):
        """ Generate values from basic types.
            Set value to target.
        """
        if fake is None:
            fake = self.fake

        gen = self.get_generator(fcls, fname, fake=fake)
        setattr(target, fname, next(gen))

    def gen_field(self, target, field_name, field):
        """
        Generate value by field.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param relation: Instance of :class:`Field`
        """
        self.gen_value(target, field_name, field.scheme)

    def gen_relation(self, target, field_name, relation):
        """
        Generate a related field by `relation`

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param relation: Instance of :class:`Relation`

        """
        mixer = TypeMixer(relation.scheme, self.mixer, self.generator)
        setattr(target, field_name, mixer.blend(**relation.params))

    def gen_random(self, target, field_name):
        """
        Generate random value of field with `field_name` for `target`

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        """
        field = self.fields.get(field_name)
        scheme = field and field.scheme or field
        self.gen_value(target, field_name, scheme, fake=False)

    gen_select = gen_random

    def gen_fake(self, target, field_name):
        """
        Generate fake value of field with `field_name` for `target`

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        """
        field = self.fields.get(field_name)
        self.gen_value(target, field_name, field.scheme, fake=True)

    def get_generator(self, field_class, field_name=None, fake=None):
        """
        Cache generator for class.

        :param field_class: Class for looking a generator
        :param field_name: Name of field for generation
        :param fake: Generate fake data instead of random data.
        """
        if fake is None:
            fake = self.fake

        key = (field_class, field_name, fake)

        if not key in self.generators:
            self.generators[key] = self.make_generator(
                field_class, field_name, fake)

        return self.generators[key]

    def make_generator(self, field_class, field_name=None, fake=None):
        """
        Make generator for class.

        :param field_class: Class for looking a generator
        :param field_name: Name of field for generation
        :param fake: Generate fake data instead of random data.
        """
        return self.generator.gen_maker(field_class, field_name, fake)()

    def __load_fields(self):
        """ Generator of scheme's fields.
        """
        for fname in dir(self.cls):
            if fname.startswith('_'):
                continue
            yield fname, Field(getattr(self.cls, fname), fname)


class MetaMixer:

    def __init__(self, mixer, count=5):
        self.count = count
        self.mixer = mixer

    def blend(self, scheme, **values):
        result = []
        for _ in range(self.count):
            result.append(
                self.mixer.blend(scheme, **values)
            )
        return result

    def __getattr__(self, name):
        raise AttributeError('Use "cycle" only for "blend"')


class Mixer(object):
    """
    This class is used for integration to one or more applications.

    :param fake: (True) Generate fake data instead of random data.

    ::
        class SomeScheme:
            score = int
            name = str

        mixer = Mixer()
        instance = mixer.blend(SomeScheme)

        print instance.name
        # Some like: 'Mike Douglass'

    """

    # system flags
    fake = FAKE
    select = SELECT
    random = RANDOM

    # generator's controller class
    type_mixer_cls = TypeMixer

    def __init__(self, fake=True, **params):
        """Initialize Mixer instance.

        :param fake: (True) Generate fake data instead of random data.

        """
        self.params = params
        self.fake = fake

    def __repr__(self):
        return "<Mixer [{0}]>".format('fake' if self.fake else 'rand')

    def blend(self, scheme, **values):
        """Generate instance of `scheme`.

        :param scheme: Scheme class for generation
        :param **values: Predefined fields

        ::
            mixer = Mixer()
            mixer.blend(SomeSheme, active=True)

            print scheme.active
            # True

        """
        type_mixer = self.type_mixer_cls(scheme, mixer=self)
        result = type_mixer.blend(**values)
        result = self.post_generate(result, type_mixer)
        for fname, fvalue in type_mixer.post_save_values.items():
            setattr(result, fname, fvalue)
        return result

    @staticmethod
    def post_generate(target, type_mixer):
        return target

    @staticmethod
    def sequence(func):
        if isinstance(func, six.string_types):
            func = func.format

        def gen():
            counter = 0
            while True:
                yield func(counter)
                counter += 1
        return gen()

    def cycle(self, count=5):
        return MetaMixer(self, count)


# Default mixer
mixer = Mixer()

# lint_ignore=C901,W0622,F0401,W0621
