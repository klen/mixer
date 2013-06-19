"""
    mixer.main
    ~~~~~~~~~~

    This module implements the objects generation.

    :copyright: 2013 by Kirill Klenov.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import, unicode_literals

import datetime
from copy import deepcopy

import decimal
from importlib import import_module
from collections import defaultdict
from types import GeneratorType

from . import generators as g, fakers as f, mix_types as t
from . import six


NO_VALUE = object()


class Mix(object):

    """ Virtual link on the mixed object.

    ::

        mixer = Mixer()

        # here `mixer.mix` points on a generated `User` instance
        user = mixer.blend(User, username=mixer.mix.first_name)

        # here `mixer.mix` points on a generated `Message.author` instance
        message = mixer.blend(Message, author__name=mixer.mix.login)

        # Mixer mix can get a function
        message = mixer.blend(Message, title=mixer.mix.author(
            lambda author: 'Author: %s' % author.name
        ))

    """

    def __init__(self, value=None, parent=None):
        self.__value = value
        self.__parent = parent
        self.__func = None

    def __getattr__(self, value):
        return Mix(value, self if self.__value else None)

    def __call__(self, func):
        self.__func = func
        return self

    def __and__(self, value):
        if self.__parent:
            value = self.__parent & value
        value = getattr(value, self.__value)
        if self.__func:
            return self.__func(value)
        return value

    def __str__(self):
        return '%s/%s' % (self.__value, str(self.__parent or ''))

    def __repr__(self):
        return '<Mix %s>' % str(self)


class ServiceValue(object):

    """ Abstract class for mixer values. """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def __call__(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def gen_value(self, type_mixer, *args, **kwargs):
        """ Abstract method for value generation. """
        raise NotImplementedError


class Field(ServiceValue):

    """ Set field values.

    By default the mixer generates random or fake a field values by types
    of them. But you can set some values by manual.

    ::

        # Generate a User model
        mixer.blend(User)

        # Generate with some values
        mixer.blend(User, name='John Connor')

    .. note:: Value may be a callable or instance of generator.

    ::

        # Value may be callable
        client = mixer.blend(Client, username=lambda:'callable_value')
        assert client.username == 'callable_value'

        # Value may be a generator
        clients = mixer.cycle(4).blend(
            Client, username=(name for name in ('Piter', 'John')))


    .. seealso:: :class:`mixer.main.Fake`, :class:`mixer.main.Random`,
                 :class:`mixer.main.Select`,
                 :meth:`mixer.main.Mixer.sequence`

    """

    is_relation = False

    def __init__(self, scheme, name):
        self.scheme = scheme
        self.name = name

    def __deepcopy__(self, memo):
        return Field(self.scheme, self.name)

    def gen_value(self, type_mixer, *args, **kwargs):
        """ Call :meth:`TypeMixer.gen_field`.

        :return value: A generated value

        """
        return type_mixer.gen_field(*args, **kwargs)


class Relation(Field):

    """ Generate a relation values.

    Some fields from a model could be a relation on other models.
    Mixer can generate this fields as well, but you can force some
    values for generated models. Use `__` for relation values.

    ::

        message = mixer.blend(Message, client__username='test2')
        assert message.client.username == 'test2'

        # more hard relation
        message = mixer.blend(Message, client__role__name='admin')
        assert message.client.role.name == 'admin'

    """

    is_relation = True

    def __init__(self, scheme, name, params=None):
        super(Relation, self).__init__(scheme, name)
        self.params = params or dict()

    def __deepcopy__(self, memo):
        return Relation(self.scheme, self.name, deepcopy(self.params))

    def gen_value(self, type_mixer, *args, **kwargs):
        """ Call :meth:`TypeMixer.gen_value`.

        :return value: A generated value

        """
        return type_mixer.gen_relation(*args, **kwargs)


# Service classes
class Fake(ServiceValue):

    """ Force a `fake` value.

    If you initialized a :class:`~mixer.main.Mixer` with `fake=False` you can
    force a `fake` value for field with this attribute (mixer.fake).

    ::

         mixer = Mixer(fake=False)
         user = mixer.blend(User)
         print user.name  # Some like: Fdjw4das

         user = mixer.blend(User, name=mixer.fake)
         print user.name  # Some like: Bob Marley

    You can setup a field type for generation of fake value: ::

         user = mixer.blend(User, score=mixer.fake(str))
         print user.score  # Some like: Bob Marley

    .. note:: This is also usefull on ORM model generation for filling a fields
              with default values (or null).

    ::

        from mixer.backend.django import mixer

        user = mixer.blend('auth.User', first_name=mixer.fake)
        print user.first_name  # Some like: John

    """

    def gen_value(self, type_mixer, *args, **kwargs):
        """ Call :meth:`TypeMixer.gen_fake`.

        :return value: A generated value

        """
        return type_mixer.gen_fake(*args, **kwargs)


class Random(ServiceValue):

    """ Force a `random` value.

    If you initialized a :class:`~mixer.main.Mixer` by default mixer try to
    fill fields with `fake` data. You can user `mixer.random` for prevent this
    behaviour for a custom fields.

    ::

         mixer = Mixer()
         user = mixer.blend(User)
         print user.name  # Some like: Bob Marley

         user = mixer.blend(User, name=mixer.random)
         print user.name  # Some like: Fdjw4das

    You can setup a field type for generation of fake value: ::

         user = mixer.blend(User, score=mixer.random(str))
         print user.score  # Some like: Fdjw4das

    .. note:: This is also usefull on ORM model generation for randomize fields
              with default values (or null).

    ::

        from mixer.backend.django import mixer

        mixer.blend('auth.User', first_name=mixer.random)
        print user.first_name  # Some like: Fdjw4das

    """

    def gen_value(self, type_mixer, *args, **kwargs):
        """ Call :meth:`TypeMixer.gen_random`.

        :return value: A generated value

        """
        return type_mixer.gen_random(*args, **kwargs)


class Select(ServiceValue):

    """ Select values from database.

    When you generate some ORM models you can set value for related fields
    from database (select by random).

    Example for Django (select user from exists): ::

        from mixer.backend.django import mixer

        mixer.generate(Role, user=mixer.select)


    You can setup a Django or SQLAlchemy filters with `mixer.select`: ::

        from mixer.backend.django import mixer

        mixer.generate(Role, user=mixer.select(
            username='test'
        ))

    """

    def gen_value(self, type_mixer, *args, **kwargs):
        """ Call :meth:`TypeMixer.gen_random`.

        :return value: A generated value

        """
        return type_mixer.gen_select(*args, **kwargs)


class GenFactoryMeta(type):

    """ Precache generators. """

    def __new__(mcs, name, bases, params):
        generators = dict()
        fakers = dict()
        types = dict()

        for cls in bases:
            if isinstance(cls, GenFactoryMeta):
                generators.update(cls.generators)
                fakers.update(cls.fakers)
                types.update(cls.types)

        generators.update(params.get('generators', dict()))
        fakers.update(params.get('fakers', dict()))
        types.update(params.get('types', dict()))

        generators = dict(mcs.__flat_keys(generators))
        types = dict(mcs.__flat_keys(types))

        params['generators'] = generators
        params['fakers'] = fakers
        params['types'] = types

        return super(GenFactoryMeta, mcs).__new__(mcs, name, bases, params)

    @staticmethod
    def __flat_keys(d):
        for key, value in d.items():
            if isinstance(key, (tuple, list)):
                for k in key:
                    yield k, value
                continue
            yield key, value


class GenFactory(six.with_metaclass(GenFactoryMeta)):

    """ Make generators for types. """

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
        t.URL: f.gen_url,
        t.UUID: f.gen_uuid,
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
        ('body', str): f.gen_lorem,
        ('city', str): f.gen_city,
        ('country', str): f.gen_country,
        ('email', str): f.gen_email,
        ('username', str): f.gen_username,
        ('login', str): f.gen_username,
        ('domain', str): f.gen_hostname,
        ('phone', str): f.gen_phone,
        ('company', str): f.gen_company,
        ('lat', float): f.gen_latlon,
        ('latitude', float): f.gen_latlon,
        ('lon', float): f.gen_latlon,
        ('longitude', float): f.gen_latlon,
    }

    types = {}

    @classmethod
    def cls_to_simple(cls, fcls):
        """ Translate class to one of simple base types.

        :return type: A simple type for generation

        """
        return cls.types.get(fcls) or (
            fcls if fcls in cls.generators
            else None
        )

    @staticmethod
    def name_to_simple(fname):
        """ Translate name to one of simple base names.

        :return str:

        """
        fname = fname or ''
        return fname.lower().strip()

    @classmethod
    def gen_maker(cls, fcls, fname=None, fake=False):
        """ Make a generator based on class and name.

        :return generator:

        """
        fcls = cls.cls_to_simple(fcls)
        fname = cls.name_to_simple(fname)

        gen_maker = cls.generators.get(fcls)

        if fname and fake and (fname, fcls) in cls.fakers:
            gen_maker = cls.fakers.get((fname, fcls)) or gen_maker

        return gen_maker


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
        if not key in cls.mixers:
            cls.mixers[key] = super(TypeMixerMeta, cls).__call__(
                cls_type, mixer=mixer, factory=factory, fake=fake,
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

    """ Generate models. """

    factory = GenFactory

    fake = Fake()
    select = Select()
    random = Random()

    def __init__(self, cls, mixer=None, factory=None, fake=True):
        self.__scheme = cls
        self.__mixer = mixer
        self.__fake = fake
        self.__fields = dict(self.__load_fields())
        self.__factory = factory or self.factory
        self.__generators = dict()
        self.__gen_values = defaultdict(set)

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
                if not isinstance(field, Relation):
                    defaults[rname] = Relation(
                        field and field.scheme or field,
                        field and field.name or rname)
                defaults[rname].params.update({rvalue: params})
                continue
            defaults[key] = params

        # Fill fields in 2 steps
        post_values = [
            item for item in [
                self.set_value(target, fname, fvalue, finaly=True)
                for (fname, fvalue) in [
                    item for item in self.fill_fields(target, defaults) if item
                ]
            ] if item
        ]

        if self.__mixer:
            target = self.__mixer.post_generate(target)

        for fname, fvalue in post_values:
            setattr(target, fname, fvalue)

        return target

    def fill_fields(self, target, defaults):
        """ Fill all required fields. """
        for fname, fvalue in defaults.items():

            if isinstance(fvalue, ServiceValue):
                yield fvalue.gen_value(self, target, fname, fvalue)

            else:
                yield self.set_value(target, fname, fvalue)

    def set_value(self, target, field_name, field_value, finaly=False):
        """ Set `value` to `target` as `field_name`.

        :return : None or (name, value) for later use

        """
        if isinstance(field_value, Mix):
            if not finaly:
                return field_name, field_value

            return self.set_value(
                target, field_name, field_value & target, finaly=finaly)

        if callable(field_value):
            return self.set_value(
                target, field_name, field_value(), finaly=finaly)

        if isinstance(field_value, GeneratorType):
            return self.set_value(
                target, field_name, next(field_value), finaly=finaly)

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

        if unique:
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
        if not default is NO_VALUE:
            return self.set_value(target, field_name, default)

        required = self.is_required(field)
        if not required:
            return False

        unique = self.is_unique(field)
        return self.gen_value(target, field_name, field.scheme, unique=unique)

    def gen_relation(self, target, field_name, relation):
        """ Generate a related field by `relation`.

        :param target: Target for generate value.
        :param field_name: Name of field for generation.
        :param relation: Instance of :class:`Relation`

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

        else:
            field = self.__fields.get(field_name)
            scheme = field and field.scheme or field

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

        if not key in self.__generators:
            self.__generators[key] = self.make_generator(
                field_class, field_name, fake)

        return self.__generators[key]

    def make_generator(self, field_class, field_name=None, fake=None):
        """ Make generator for class.

        :param field_class: Class for looking a generator
        :param field_name: Name of field for generation
        :param fake: Generate fake data instead of random data.

        :return generator:

        """
        return self.__factory.gen_maker(field_class, field_name, fake)()

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

    def __load_fields(self):
        """ GenFactory of scheme's fields. """
        for fname in dir(self.__scheme):
            if fname.startswith('_'):
                continue
            yield fname, Field(getattr(self.__scheme, fname), fname)


class MetaMixer:

    """ A Mixer proxy. Using for generate a few objects.

    ::

        mixer.cycle(5).blend(somemodel)

    """

    def __init__(self, mixer, count=5):
        self.count = count
        self.mixer = mixer

    def blend(self, scheme, **values):
        """ Call :meth:`Mixer.blend` a few times. And stack results to list.

        :return list: list of generated objects.

        """
        result = []
        for _ in range(self.count):
            result.append(
                self.mixer.blend(scheme, **values)
            )
        return result

    def __getattr__(self, name):
        raise AttributeError('Use "cycle" only for "blend"')


class Mixer(object):

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

    #: Force a fake values. See :class:`~mixer.main.Fake`
    fake = Fake()

    #: Force a random values. See :class:`~mixer.main.Random`
    random = Random()

    #: Select a data from databases. See :class:`~mixer.main.Select`
    select = Select()

    #: Points to a mixed object from future. See :class:`~mixer.main.Mix`
    mix = Mix()

    # generator's controller class
    type_mixer_cls = TypeMixer

    def __init__(self, fake=True, factory=None, **params):
        """Initialize Mixer instance.

        :param fake: (True) Generate fake data instead of random data.
        :param factory: (:class:`~mixer.main.GenFactory`) A class for
                          generation values for types

        """
        self.params = params
        self.factory = factory
        self.fake = fake

    def __repr__(self):
        return "<Mixer [{0}]>".format('fake' if self.fake else 'rand')

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
        type_mixer = self.type_mixer_cls(
            scheme, mixer=self, fake=self.fake, factory=self.factory)
        return type_mixer.blend(**values)

    @staticmethod
    def post_generate(target):
        """ Post processing a generated value.

        :return value:

        """
        return target

    @staticmethod
    def sequence(func=None):
        """ Create sequence for predefined values.

        It makes a infinity loop with given function where does increment the
        counter on each iteration.

        :param func: If func is equal string it should be using as format
                        string.

                        By default function is equal 'lambda x: x'.

        :type func: Function from one argument or format string.
        :return generator:

        Mixer can uses a generators.
        ::

            gen = (name for name in ['test0', 'test1', 'test2'])
            for counter in range(3):
                mixer.blend(Scheme, name=gen)

        Mixer.sequence is a helper for create generators from functions.
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
        if isinstance(func, six.string_types):
            func = func.format

        elif func is None:
            func = lambda x: x

        def gen():
            counter = 0
            while True:
                yield func(counter)
                counter += 1
        return gen()

    def cycle(self, count=5):
        """ Generate a few objects. Syntastic sugar for cycles.

        :param count: List of objects or integer.
        :return MetaMixer:

        ::

            users = mixer.cycle(5).blend('somemodule.User')

            profiles = mixer.cycle(5).blend(
                'somemodule.Profile', user=(user for user in users)

            apples = mixer.cycle(10).blend(
                Apple, title=mixer.sequence('apple_{0}')

        """
        return MetaMixer(self, count)


# Default mixer
mixer = Mixer()

# lint_ignore=C901,W0622,F0401,W0621,W0231,E1002
