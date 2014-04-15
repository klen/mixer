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


NO_VALUE = object()
SKIP_VALUE = object()

LOGLEVEL = logging.WARN
LOGGER = logging.getLogger('mixer')
if not LOGGER.handlers and not LOGGER.root.handlers:
    LOGGER.addHandler(logging.StreamHandler())


class TypeMixerMeta(type):

    """ Cache mixers by class. """

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
                cls_type, mixer=mixer, factory=factory, fake=fake
            )
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
        self.postprocess = None
        self.__scheme = cls
        self.__mixer = mixer
        self.__fake = fake
        self.__factory = factory or self.factory
        self.__generators = dict()
        self.__gen_values = defaultdict(set)
        self.__fields = OrderedDict(self.__load_fields())

    def __repr__(self):
        return "<TypeMixer {0}>".format(self.__scheme)

    def blend(self, **values):
        """ Generate instance.

        :param **values: Predefined fields
        :return value: a generated value

        """
        target = self.__scheme()

        defaults = deepcopy(self.__fields)

        # Prepare relations
        for key, params in values.items():
            if '__' in key:
                rname, rvalue = key.split('__', 1)
                field = defaults.get(rname)
                if not field or not field.is_relation:
                    defaults[rname] = t.Relation(
                        field and field.scheme or field,
                        field and field.name or rname)
                defaults[rname].params.update({rvalue: params})
                continue
            defaults[key] = params

        deferred_values = list(self.fill_fields(target, defaults))

        # Fill fields in 2 steps
        post_values = [
            item for item in [
                self.set_value(target, fname, fvalue, finaly=True)
                for (fname, fvalue) in deferred_values
            ] if item
        ]

        if self.postprocess:
            target = self.postprocess(target)  # noqa

        if self.__mixer:
            target = self.__mixer.post_generate(target)

        for fname, fvalue in post_values:
            self.set_value(target, fname, fvalue)

        LOGGER.info('Blended: %s [%s]', target, self.__scheme) # noqa
        return target

    def fill_fields(self, target, defaults):
        """ Fill all required fields. """
        for fname, fvalue in defaults.items():

            if isinstance(fvalue, t.ServiceValue):
                deferred = fvalue.gen_value(self, target, fname, fvalue)

            else:
                deferred = self.set_value(target, fname, fvalue)

            if deferred:
                yield deferred

    def set_value(self, target, field_name, field_value, finaly=False):
        """ Set `value` to `target` as `field_name`.

        :return : None or (name, value) for later use

        """
        if field_value is SKIP_VALUE:
            return

        if isinstance(field_value, GeneratorType):
            return self.set_value(
                target, field_name, next(field_value), finaly=finaly)

        if isinstance(field_value, t.Mix):
            if not finaly:
                return field_name, field_value

            return self.set_value(
                target, field_name, field_value & target, finaly=finaly)

        if callable(field_value):
            return self.set_value(
                target, field_name, field_value(), finaly=finaly)

        setattr(target, field_name, field_value)

    def gen_value(self, target, field_name, field_class, fake=None,
                  unique=False):
        """ Generate values from basic types.

        Set value to target.

        :return : None or (name, value) for later use

        """
        fake = self.__fake if fake is None else fake
        gen = self.get_generator(field_class, field_name, fake=fake)
        value = next(gen)

        if unique and value is not SKIP_VALUE:
            counter = 0
            while value in self.__gen_values[field_class]:
                value = next(gen)
                counter += 1
                if counter > 100:
                    raise RuntimeError(
                        "Cannot generate a unique value for %s" % field_name
                    )
            self.__gen_values[field_class].add(value)

        return self.set_value(target, field_name, value)

    def gen_field(self, target, field_name, field):
        """ Generate value by field.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param relation: Instance of :class:`Field`

        :return : None or (name, value) for later use

        """
        default = self.get_default(field, target)

        if default is not NO_VALUE:
            return self.set_value(target, field_name, default)

        if not self.is_required(field):
            return False

        unique = self.is_unique(field)
        return self.gen_value(target, field_name, field.scheme, unique=unique)

    def gen_relation(self, target, field_name, relation, force=False):
        """ Generate a related field by `relation`.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param relation: Instance of :class:`Relation`
        :param force: Force a value generation

        :return : None or (name, value) for later use

        """
        mixer = TypeMixer(relation.scheme, self.__mixer, self.__factory)
        return self.set_value(
            target, field_name, mixer.blend(**relation.params))

    def gen_random(self, target, field_name, field_value):
        """ Generate random value of field with `field_name` for `target`.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param field_value: Instance of :class:`~mixer.main.Random`.

        :return : None or (name, value) for later use

        """
        if field_value.args:
            scheme = field_value.args[0]

            if not isinstance(scheme, type):
                return self.set_value(
                    target, field_name, g.get_choice(field_value.args))

        else:
            scheme = self.__fields.get(field_name)
            if scheme:

                if scheme.is_relation:
                    return self.gen_relation(target, field_name, scheme, True)

                scheme = scheme.scheme

        return self.gen_value(target, field_name, scheme, fake=False)

    gen_select = gen_random

    def gen_fake(self, target, field_name, field_value):
        """ Generate fake value of field with `field_name` for `target`.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param field_value: Instance of :class:`~mixer.main.Fake`.

        :return : None or (name, value) for later use

        """
        if field_value.args:
            scheme = field_value.args[0]

        else:
            field = self.__fields.get(field_name)
            scheme = field and field.scheme or field

        return self.gen_value(target, field_name, scheme, fake=True)

    def get_generator(self, field_class, field_name=None, fake=None):
        """ Get generator for field and cache it.

        :param field_class: Class for looking a generator
        :param field_name: Name of field for generation
        :param fake: Generate fake data instead of random data.

        :return generator:

        """
        if fake is None:
            fake = self.__fake

        key = (field_class, field_name, fake)

        if key not in self.__generators:
            self.__generators[key] = self.make_generator(
                field_class, field_name, fake)

        return self.__generators[key]

    def make_generator(self, field_class, field_name=None, fake=None, args=[], kwargs={}): # noqa
        """ Make generator for class.

        :param field_class: Class for looking a generator
        :param field_name: Name of field for generation
        :param fake: Generate fake data instead of random data.

        :return generator:

        """
        fabric = self.__factory.gen_maker(field_class, field_name, fake)
        if fabric:
            gen = fabric(*args, **kwargs)
        else:
            gen = self.__factory.generators.get(None)
        return (
            gen if isinstance(gen, GeneratorType)
            else g.loop(fabric)(*args, **kwargs)
        )

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

        field_class = self.__fields.get(field_name)
        if field_class:
            key = (field_class.scheme, field_name, fake)
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
    def get_default(field, target):
        """ Get default value from field.

        :return value:

        """
        return NO_VALUE

    @staticmethod
    def guard(**filters):
        """ Look objects in storage.

        :returns: False

        """
        return False

    def __load_fields(self):
        """ GenFactory of scheme's fields. """
        for fname in dir(self.__scheme):
            if fname.startswith('_'):
                continue
            prop = getattr(self.__scheme, fname)
            if not self.__factory.generators.get(prop):
                yield fname, t.Relation(prop, fname)
            else:
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
        except Exception:
            if self.params.get('silence'):
                return None
            raise

    def get_typemixer(self, scheme):
        """ Return cached typemixer instance.

        :return TypeMixer:

        """
        return self.type_mixer_cls(
            scheme, mixer=self,
            fake=self.params.get('fake'), factory=self.__factory)

    @staticmethod
    def post_generate(target):
        """ Post processing a generated value.

        :return value:

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

    def register(self, scheme, params=None, fake=None, postprocess=None):
        """ Manualy register a function as value's generator for class.field.

        :param scheme: Scheme class for generation or string with class path.
        :param fake: Register as fake generator
        :param postprocess: Callback for postprocessing value (lambda obj: ...)
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
        if fake is None:
            fake = self.params.get('fake')

        type_mixer = self.type_mixer_cls(
            scheme, mixer=self, fake=self.params.get('fake'),
            factory=self.__factory)

        if postprocess:
            type_mixer.postprocess = postprocess

        if params:
            for field_name, func in params.items():
                type_mixer.register(field_name, func, fake=fake)

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

    def guard(self, **guards):
        """ Abstract method. In some backends used for prevent object creation.

        :returns: A Proxy to mixer

        """
        return ProxyMixer(self, count=1, guards=guards)

    def _guard(self, scheme, guards, **values):
        type_mixer = self.get_typemixer(scheme)
        seek = type_mixer.guard(**guards)
        if seek:
            LOGGER.info('Finded: %s [%s]', seek, type(seek)) # noqa
            return seek

        guards.update(values)
        return self.blend(scheme, **guards)


# Default mixer
mixer = Mixer()
