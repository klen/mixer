""" Base for custom backends.

mixer.main
~~~~~~~~~~

This module implements the objects generation.

:copyright: 2013 by Kirill Klenov.
:license: BSD, see LICENSE for more details.

"""
from __future__ import absolute_import, unicode_literals

import warnings
from types import GeneratorType

import logging
import traceback
from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from importlib import import_module

from . import generators as g, fakers as f, mix_types as t, _compat as _
from .factory import GenFactory


try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict # noqa


SKIP_VALUE = object()

LOGLEVEL = logging.WARN
LOGGER = logging.getLogger('mixer')
if not LOGGER.handlers and not LOGGER.root.handlers:
    LOGGER.addHandler(logging.StreamHandler())


class _Deffered(object):

    """ Post process value. """

    def __init__(self, value, scheme=None):
        self.value = value
        self.scheme = scheme


class TypeMixerMeta(type):

    """ Cache type mixers by scheme. """

    mixers = dict()

    def __call__(cls, cls_type, mixer=None, factory=None, fake=True):
        backup = cls_type
        try:
            cls_type = cls.__load_cls(cls_type)
            assert cls_type
        except (AttributeError, AssertionError):
            raise ValueError('Invalid scheme: %s' % backup)

        key = (mixer, cls_type, fake, factory)
        if key not in cls.mixers:
            cls.mixers[key] = super(TypeMixerMeta, cls).__call__(
                cls_type, mixer=mixer, factory=factory, fake=fake)

        return cls.mixers[key]

    @staticmethod
    def __load_cls(cls_type):
        if isinstance(cls_type, _.string_types):
            mod, cls_type = cls_type.rsplit('.', 1)
            mod = import_module(mod)
            cls_type = getattr(mod, cls_type)
        return cls_type


class TypeMixer(_.with_metaclass(TypeMixerMeta)):

    """ Generate models. """

    factory = GenFactory

    FAKE = property(lambda s: Mixer.FAKE)
    MIX = property(lambda s: Mixer.MIX)
    RANDOM = property(lambda s: Mixer.RANDOM)
    SELECT = property(lambda s: Mixer.SELECT)
    SKIP = property(lambda s: Mixer.SKIP)

    def __init__(self, cls, mixer=None, factory=None, fake=True):
        self.middlewares = []
        self.__factory = factory or self.factory
        self.__fake = fake
        self.__gen_values = defaultdict(set)
        self.__generators = dict()
        self.__mixer = mixer
        self.__scheme = cls

        self.__fields = OrderedDict(self.__load_fields())

    def __repr__(self):
        return "<TypeMixer {0}>".format(self.__scheme)

    def blend(self, **values):
        """ Generate instance.

        :param **values: Predefined fields
        :return value: a generated value

        """
        defaults = deepcopy(self.__fields)

        # Prepare relations
        for key, params in values.items():
            if '__' in key:
                name, value = key.split('__', 1)
                if name not in defaults:
                    defaults[name] = t.Field(None, name)
                defaults[name].params.update({value: params})
                continue
            defaults[key] = params

        values = dict(
            value.gen_value(self, name, value)
            if isinstance(value, t.ServiceValue)
            else self.get_value(name, value)
            for name, value in defaults.items()
        )

        # Parse MIX and SKIP values
        candidates = list(
            (name, value & values if isinstance(value, t.Mix) else value)
            for name, value in values.items()
            if value is not SKIP_VALUE
        )

        values = list()
        postprocess_values = list()
        for name, value in candidates:
            if isinstance(value, _Deffered):
                postprocess_values.append((name, value))
            else:
                values.append((name, value))

        target = self.populate_target(values)

        # Run registered middlewares
        for middleware in self.middlewares:
            target = middleware(target)

        target = self.postprocess(target, postprocess_values)

        LOGGER.info('Blended: %s [%s]', target, self.__scheme) # noqa
        return target

    def postprocess(self, target, postprocess_values):
        """ Run postprocess code. """
        if self.__mixer:
            target = self.__mixer.postprocess(target)

        for name, deffered in postprocess_values:
            setattr(target, name, deffered.value)

        return target

    def populate_target(self, values):
        """ Populate target with values. """
        target = self.__scheme()
        for name, value in values:
            setattr(target, name, value)
        return target

    def get_value(self, name, value):
        """ Parse field value.

        :return : (name, value) or None

        """
        if isinstance(value, GeneratorType):
            return self.get_value(name, next(value))

        if callable(value) and not isinstance(value, t.Mix):
            return self.get_value(name, value())

        return name, value

    def gen_field(self, field):
        """ Generate value by field.

        :param field: Instance of :class:`Field`

        :return : None or (name, value) for later use

        """
        default = self.get_default(field)

        if default is not SKIP_VALUE:
            return self.get_value(field.name, default)

        if not self.is_required(field):
            return field.name, SKIP_VALUE

        unique = self.is_unique(field)
        return self.gen_value(field.name, field, unique=unique)

    def gen_random(self, field_name, random):
        """ Generate random value of field with `field_name`.

        :param field_name: Name of field for generation.
        :param random: Instance of :class:`~mixer.main.Random`.

        :return : None or (name, value) for later use

        """
        if not random.scheme:
            random = deepcopy(self.__fields.get(field_name))

        elif not isinstance(random.scheme, type):
            return self.get_value(field_name, g.get_choice(random.choices))

        return self.gen_value(field_name, random, fake=False)

    gen_select = gen_random

    def gen_fake(self, field_name, fake):
        """ Generate fake value of field with `field_name`.

        :param field_name: Name of field for generation.
        :param fake: Instance of :class:`~mixer.main.Fake`.

        :return : None or (name, value) for later use

        """
        if not fake.scheme:
            fake = deepcopy(self.__fields.get(field_name))

        return self.gen_value(field_name, fake, fake=True)

    def gen_value(self, field_name, field, fake=None, unique=False):
        """ Generate values from basic types.

        :return : (name, value) for later use

        """
        fake = self.__fake if fake is None else fake
        if field:
            gen = self.get_generator(field, field_name, fake=fake)
        else:
            gen = self.__factory.gen_maker(type(field))()

        try:
            value = next(gen)
        except ValueError:
            value = None

        if unique and value is not SKIP_VALUE:
            counter = 0
            while value in self.__gen_values[field_name]:
                value = next(gen)
                counter += 1
                if counter > 100:
                    raise RuntimeError("Cannot generate a unique value for %s" % field_name)
            self.__gen_values[field_name].add(value)

        return self.get_value(field_name, value)

    def get_generator(self, field, field_name=None, fake=None):
        """ Get generator for field and cache it.

        :param field: Field for looking a generator
        :param field_name: Name of field for generation
        :param fake: Generate fake data instead of random data.

        :return generator:

        """
        if fake is None:
            fake = self.__fake

        if field.params:
            return self.make_generator(
                field.scheme, field_name, fake, kwargs=field.params)

        key = (field.scheme, field_name, fake)

        if key not in self.__generators:
            self.__generators[key] = self.make_generator(
                field.scheme, field_name, fake, kwargs=field.params)

        return self.__generators[key]

    def make_generator(self, scheme, field_name=None, fake=None, args=None, kwargs=None): # noqa
        """ Make generator for class.

        :param field_class: Class for looking a generator
        :param scheme: Scheme for generation
        :param fake: Generate fake data instead of random data.

        :return generator:

        """
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs

        fabric = self.__factory.gen_maker(scheme, field_name, fake)
        if not fabric:
            return g.loop(self.__class__(
                scheme, mixer=self.__mixer, fake=self.__fake,
                factory=self.__factory).blend)(**kwargs)

        return fabric(*args, **kwargs)

    def register(self, field_name, func, fake=None):
        """ Register function as generator for field.

        :param field_name: Name of field for generation
        :param func: Function for data generation
        :param fake: Generate fake data instead of random data.

        ::

            class Scheme:
                id = str

            def func():
                return 'ID'

            mixer = TypeMixer(Scheme)
            mixer.register('id', func)

            test = mixer.blend()
            test.id == 'id'

        """
        if fake is None:
            fake = self.__fake

        field = self.__fields.get(field_name)
        if field:
            key = (field.scheme, field_name, fake)
            self.__generators[key] = g.loop(func)()

    @staticmethod
    def is_unique(field):
        """ Return True is field's value should be a unique.

        :return bool:

        """
        return False

    @staticmethod
    def is_required(field):
        """ Return True is field's value should be defined.

        :return bool:

        """
        return True

    @staticmethod
    def get_default(field):
        """ Get default value from field.

        :return value:

        """
        return SKIP_VALUE

    @staticmethod
    def guard(*args, **kwargs):
        """ Look objects in storage.

        :returns: False

        """
        return False

    def reload(self, obj):
        """ Reload the object from storage. """
        return deepcopy(obj)

    def __load_fields(self):
        """ Find scheme's fields. """
        for fname in dir(self.__scheme):
            if fname.startswith('_'):
                continue
            prop = getattr(self.__scheme, fname)
            yield fname, t.Field(prop, fname)


class ProxyMixer:

    """ A Mixer proxy. Using for generate a few objects.

    ::

        mixer.cycle(5).blend(somemodel)

    """

    def __init__(self, mixer, count=5, guards=None):
        self.count = count
        self.mixer = mixer
        self.guards = guards

    def blend(self, scheme, **values):
        """ Call :meth:`Mixer.blend` a few times. And stack results to list.

        :returns: A list of generated objects.

        """
        result = []

        if self.guards:
            return self.mixer._guard(scheme, self.guards, **values) # noqa

        for _ in range(self.count):
            result.append(
                self.mixer.blend(scheme, **values)
            )
        return result

    def __getattr__(self, name):
        raise AttributeError('Use "cycle" only for "blend"')


# Support depricated attributes
class _MetaMixer(type):

    F = property(lambda cls: f)
    FAKE = property(lambda cls: t.Fake())
    G = property(lambda cls: g)
    MIX = property(lambda cls: t.Mix())
    RANDOM = property(lambda cls: t.Random())
    SELECT = property(lambda cls: t.Select())
    SKIP = property(lambda cls: SKIP_VALUE)


class Mixer(_.with_metaclass(_MetaMixer)):

    """ This class is used for integration to one or more applications.

    :param fake: (True) Generate fake data instead of random data.
    :param factory: (:class:`~mixer.main.GenFactory`) Fabric of generators
                        for types values

    ::

        class SomeScheme:
            score = int
            name = str

        mixer = Mixer()
        instance = mixer.blend(SomeScheme)
        print instance.name  # Some like: 'Mike Douglass'

        mixer = Mixer(fake=False)
        instance = mixer.blend(SomeScheme)
        print instance.name  # Some like: 'AKJfdjh3'

    """

    # generator's controller class
    type_mixer_cls = TypeMixer

    def __init__(self, fake=True, factory=None, loglevel=LOGLEVEL,
                 silence=False, **params):
        """Initialize Mixer instance.

        :param fake: (True) Generate fake data instead of random data.
        :param loglevel: ('WARN') Set level for logging
        :param silence: (False) Don't raise any errors if creation was falsed
        :param factory: (:class:`~mixer.main.GenFactory`) A class for
                          generation values for types

        """
        self.params = params
        self.__init_params__(fake=fake, loglevel=loglevel, silence=silence)
        self.__factory = factory

    def __getattr__(self, name):
        if name in ['f', 'g', 'fake', 'random', 'mix', 'select']:
            warnings.warn('"mixer.%s" is depricated, use "mixer.%s" instead.'
                          % (name, name.upper()), stacklevel=2)
            name = name.upper()
            return getattr(self, name)
        raise AttributeError("Attribute %s not found." % name)

    @property
    def SKIP(self, *args, **kwargs):
        """ Skip field generation.

        ::
            # Don't generate field 'somefield'
            mixer.blend(SomeScheme, somefield=mixer.skip)

        :returns: SKIP_VALUE

        """
        return SKIP_VALUE

    @property
    def FAKE(self, *args, **kwargs):
        """ Force a fake values. See :class:`~mixer.main.Fake`.

        :returns: Fake object

        """
        return self.__class__.FAKE

    @property
    def RANDOM(self, *args, **kwargs):
        """ Force a random values. See :class:`~mixer.main.Random`.

        :returns: Random object

        """
        return self.__class__.RANDOM

    @property
    def SELECT(self, *args, **kwargs):
        """ Select a data from databases. See :class:`~mixer.main.Select`.

        :returns: Select object

        """
        return self.__class__.SELECT

    @property
    def MIX(self, *args, **kwargs):
        """ Point to a mixed object from future. See :class:`~mixer.main.Mix`.

        :returns: Mix object

        """
        return self.__class__.MIX

    @property
    def F(self):
        """ Shortcut to :mod:`mixer.fakers`.

        ::

            mixer.F.get_name()  # -> Pier Lombardin

        :returns: fakers module

        """
        return self.__class__.F

    @property
    def G(self):
        """ Shortcut to :mod:`mixer.generators`.

        ::

            mixer.G.get_date()  # -> datetime.date(1984, 12, 12)

        :returns: generators module

        """
        return self.__class__.G

    def __init_params__(self, **params):
        self.params.update(params)
        LOGGER.setLevel(self.params.get('loglevel'))

    def __repr__(self):
        return "<Mixer [{0}]>".format(
            'fake' if self.params.get('fake') else 'rand')

    def blend(self, scheme, **values):
        """Generate instance of `scheme`.

        :param scheme: Scheme class for generation or string with class path.
        :param values: Keyword params with predefined values
        :return value: A generated instance

        ::

            mixer = Mixer()

            mixer.blend(SomeSheme, active=True)
            print scheme.active  # True

            mixer.blend('module.SomeSheme', active=True)
            print scheme.active  # True

        """
        type_mixer = self.get_typemixer(scheme)
        try:
            return type_mixer.blend(**values)
        except Exception as e:
            if self.params.get('silence'):
                return None
            e.args = ('Mixer (%s): %s' % (scheme, e.args[0]),) + e.args[1:]
            LOGGER.error(traceback.format_exc())
            raise

    def get_typemixer(self, scheme):
        """ Return cached typemixer instance.

        :return TypeMixer:

        """
        return self.type_mixer_cls(
            scheme, mixer=self,
            fake=self.params.get('fake'), factory=self.__factory)

    @staticmethod
    def postprocess(target):
        """ Post processing a generated value.

        :return target:

        """
        return target

    @staticmethod # noqa
    def sequence(*args):
        """ Create sequence for predefined values.

        It makes a infinity loop with given function where does increment the
        counter on each iteration.

        :param *args: If method get more one arguments, them make generator
                      from arguments (loop on arguments). If that get one
                      argument and this equal a function, method makes
                      a generator from them. If argument is equal string it
                      should be using as format string.

                      By default function is equal 'lambda x: x'.

        :returns: A generator

        Mixer can uses a generators.
        ::

            gen = (name for name in ['test0', 'test1', 'test2'])
            for counter in range(3):
                mixer.blend(Scheme, name=gen)

        Mixer.sequence is a helper for create generators more easy.

        Generate values from sequence:
        ::

            for _ in range(3):
                mixer.blend(Scheme, name=mixer.sequence('john', 'mike'))


        Make a generator from function:
        ::

            for counter in range(3):
                mixer.blend(Scheme, name=mixer.sequence(
                    lambda c: 'test%s' % c
                ))


        Short format is a python formating string
        ::

            for counter in range(3):
                mixer.blend(Scheme, name=mixer.sequence('test{0}'))

        """
        if len(args) > 1:
            def gen():
                while True:
                    for o in args:
                        yield o
            return gen()

        func = args and args[0] or None
        if isinstance(func, _.string_types):
            func = func.format

        elif func is None:
            func = lambda x: x

        def gen2():
            counter = 0
            while True:
                yield func(counter)
                counter += 1
        return gen2()

    def cycle(self, count=5):
        """ Generate a few objects. Syntastic sugar for cycles.

        :param count: List of objects or integer.
        :returns: ProxyMixer

        ::

            users = mixer.cycle(5).blend('somemodule.User')

            profiles = mixer.cycle(5).blend(
                'somemodule.Profile', user=(user for user in users)

            apples = mixer.cycle(10).blend(
                Apple, title=mixer.sequence('apple_{0}')

        """
        return ProxyMixer(self, count)

    def middleware(self, scheme):
        """ Middleware decorator.

        You can add middleware layers to process generation: ::

        ::

            from mixer.backend.django import mixer

            # Register middleware to model
            @mixer.middleware('auth.user')
            def encrypt_password(user):
                user.set_password('test')
                return user


        You can add several middlewares.
        Each middleware should get one argument (generated value) and return
        them.

        """
        type_mixer = self.type_mixer_cls(
            scheme, mixer=self, fake=self.params.get('fake'),
            factory=self.__factory)

        def wrapper(middleware):
            type_mixer.middlewares.append(middleware)

        return wrapper

    def register(self, scheme, **params):
        """ Manualy register a function as value's generator for class.field.

        :param scheme: Scheme class for generation or string with class path.
        :param params: dict of generators for fields. Keys are field's names.
                        Values is function without argument or objects.

        ::

            class Scheme:
                id = str
                title = str

            def func():
                return 'ID'

            mixer.register(Scheme, {
                'id': func
                'title': 'Always same'
            })

            test = mixer.blend(Scheme)
            test.id == 'ID'
            test.title == 'Always same'

        """
        fake = self.params.get('fake')
        type_mixer = self.type_mixer_cls(
            scheme, mixer=self, fake=fake, factory=self.__factory)

        for field_name, func in params.items():
            type_mixer.register(field_name, func, fake=fake)

            # Double register for RANDOM
            if fake:
                type_mixer.register(field_name, func, fake=False)

    @contextmanager
    def ctx(self, **params):
        """ Redifine params for current mixer on context.

        ::

            with mixer.ctx(commit=False):
                hole = mixer.blend(Hole)
                self.assertTrue(hole)
                self.assertFalse(Hole.objects.count())

        """
        _params = deepcopy(self.params)
        try:
            self.__init_params__(**params)
            yield self
        finally:
            self.__init_params__(**_params)

    def reload(self, *objs):
        """ Reload the objects from storage. """
        results = []
        for obj in objs:
            scheme = type(obj)
            tm = self.get_typemixer(scheme)
            results.append(tm.reload(obj))

        return results if len(results) > 1 else results[0]

    def guard(self, *args, **kwargs):
        """ Abstract method. In some backends used for prevent object creation.

        :returns: A Proxy to mixer

        """
        return ProxyMixer(self, count=1, guards=(args, kwargs))

    def _guard(self, scheme, guards, **values):
        type_mixer = self.get_typemixer(scheme)
        args, kwargs = guards
        seek = type_mixer.guard(*args, **kwargs)
        if seek:
            LOGGER.info('Finded: %s [%s]', seek, type(seek)) # noqa
            return seek

        return self.blend(scheme, **values)


# Default mixer
mixer = Mixer()

# pylama:ignore=E1120
