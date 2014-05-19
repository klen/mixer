""" Test mixer base functionality. """
import datetime

import pytest
from decimal import Decimal

from mixer.main import Mixer, TypeMixer


class Test:

    """ Model scheme for base tests. """

    one = int
    two = int
    name = str
    title = str
    body = str
    price = Decimal
    choices = list
    parts = set
    scheme = dict


def test_generators():
    """ Test random generators. """
    from mixer import generators as g

    test = next(g.gen_choice((1, 2, 3)))
    assert test in (1, 2, 3)

    test = next(g.gen_date())
    assert isinstance(test, datetime.date)

    min_date, max_date = (2010, 1, 1), (2011, 1, 1)
    test = next(g.gen_date(min_date, max_date))
    assert 2010 <= test.year <= 2011

    test = next(g.gen_date(
        datetime.date(*min_date), datetime.date(*max_date)))
    assert 2010 <= test.year <= 2011

    test = next(g.gen_time())
    assert isinstance(test, datetime.time)

    min_time, max_time = (14, 30), (15, 30)
    test = next(g.gen_time(min_time, max_time))
    assert 14 <= test.hour <= 15

    test = next(g.gen_time(
        datetime.time(*min_time), datetime.time(*max_time)))
    assert 14 <= test.hour <= 15

    test = next(g.gen_datetime())
    assert isinstance(test, datetime.datetime)

    test = next(g.gen_integer())
    assert -2147483647 <= test < 2147483647

    test = next(g.gen_big_integer())
    assert -9223372036854775808 <= test < 9223372036854775808

    test = next(g.gen_small_integer())
    assert -32768 <= test < 32768

    test = next(g.gen_positive_integer())
    assert test >= 0

    test = next(g.gen_small_positive_integer())
    assert test >= 0

    test = next(g.gen_float())
    assert test

    test = next(g.gen_boolean())
    assert test in (True, False)

    test = next(g.gen_string())
    assert test

    test = next(g.gen_decimal())
    assert test

    test = next(g.gen_positive_decimal())
    assert test

    test = next(g.gen_positive_decimal(i=2))
    assert test < 100

    test = next(g.gen_percent())
    assert 0 <= test <= 100

    test = next(g.gen_percent_decimal())
    assert 0.01 <= test <= 1.00


def test_fakers():
    """ Test default fakers. """
    from mixer import fakers as f

    test = next(f.gen_name())
    assert test

    test = next(f.gen_city())
    assert test

    test = next(f.gen_lorem(length=30))
    assert len(test) <= 30

    test = next(f.gen_numerify('##-####'))
    assert test

    test = next(f.gen_username(length=50))
    assert test

    test = next(f.gen_simple_username(length=50))
    assert test

    test = next(f.gen_hostname())
    assert test

    test = next(f.gen_email())
    assert test

    test = next(f.gen_email(host='gmail'))
    assert 'gmail' in test

    test = next(f.gen_ip4())
    assert '.' in test

    test = next(f.gen_url())
    assert '/' in test

    test = next(f.gen_uuid())
    assert '-' in test

    test = next(f.gen_phone())
    assert '-' in test

    test = next(f.gen_company())
    assert test

    test = next(f.gen_latlon())
    assert test

    test = next(f.gen_coordinates())
    assert test

    test = next(f.gen_city())
    assert test

    test = next(f.gen_genre())
    assert test

    test = next(f.gen_short_lorem())
    assert test

    test = next(f.gen_slug())
    assert test

    test = next(f.gen_street())
    assert test

    test = next(f.gen_address())
    assert test


def test_factory():
    """ Test base generator's factory. """
    from mixer.main import GenFactory

    g = GenFactory()
    test = g.gen_maker(int)()
    assert -2147483647 <= next(test) < 2147483647

    test = g.gen_maker(bool)()
    assert next(test) in (True, False)


def test_typemixer_meta():
    """ Tests that typemixer is a singleton for current class. """
    mixer1 = TypeMixer(Test)
    mixer2 = TypeMixer(Test, fake=False)
    mixer3 = TypeMixer(Test, fake=False)

    assert mixer1 is not mixer2
    assert mixer2 is mixer3


def test_typemixer():

    class Scheme:
        id = int
        name = str
        money = int
        male = bool
        prop = Test

    mixer = TypeMixer(Scheme)
    test = mixer.blend(prop__two=2, prop__one=1, prop__name='sigil', name='RJ')
    assert test.male in (True, False)
    assert test.name == 'RJ'
    assert test.prop.two == 2
    assert test.prop.name == 'sigil'

    test = mixer.blend(prop__two=4, unknown=lambda: '?')
    assert test.prop.two == 4
    assert test.unknown == '?'


def test_fake():
    from mixer.main import mixer

    test = mixer.blend(Test, name=mixer.FAKE, title=mixer.FAKE)
    assert ' ' in test.name
    assert ' ' in test.title

    test = mixer.blend(Test, name=mixer.FAKE(bool))
    assert test.name in (True, False)


def test_random():
    from mixer._compat import string_types

    mixer = TypeMixer(Test)
    test = mixer.blend(name=mixer.RANDOM)
    assert isinstance(test.name, string_types)
    assert ' ' not in test.name

    test = mixer.blend(name=mixer.RANDOM(int))
    assert isinstance(test.name, int)

    names = ['john_', 'kenn_', 'lenny_']
    test = mixer.blend(name=mixer.RANDOM(*names))
    assert test.name in names


def test_mix():
    from mixer.main import mixer

    lama = type('One', tuple(), dict(
        two=int,
        one=type('Two', tuple(), dict(two=2.1))
    ))
    mix = mixer.MIX.one.two
    assert mix & lama == 2.1

    test = mixer.blend(lama, one__two=2.1)
    assert test.one.two == 2.1
    assert test.two != test.one.two

    test = mixer.blend(lama, one__two=2.1, two=mixer.MIX.one.two)
    assert test.two == test.one.two


def test_mixer():
    mixer = Mixer()

    assert Mixer.SKIP == mixer.SKIP
    try:
        Mixer.SKIP = 111
        raise AssertionError('test are failed')
    except AttributeError:
        pass
    try:
        mixer.SKIP = 111
        raise AssertionError('test are failed')
    except AttributeError:
        pass

    gen = ('test{0}'.format(i) for i in range(500))
    test = mixer.blend('tests.test_main.Test', name=gen)
    assert test.name == 'test0'

    name_gen = mixer.sequence(lambda c: 'test' + str(c))
    test = mixer.blend(Test, name=name_gen)
    test = mixer.blend(Test, name=name_gen)
    test = mixer.blend(Test, name=name_gen)
    assert test.name == 'test2'

    name_gen = mixer.sequence('test{0}')
    test = mixer.blend(Test, name=name_gen)
    test = mixer.blend(Test, name=name_gen)
    assert test.name == 'test1'

    name_gen = mixer.sequence()
    test = mixer.blend(Test, name=name_gen)
    test = mixer.blend(Test, name=name_gen)
    assert test.name == 1

    mixer.register('tests.test_main.Test',
                   name='Michel', one=lambda: 'ID', unknown="No error here")
    test = mixer.blend(Test)
    assert test.one == 'ID'
    assert test.name == 'Michel'


def test_mixer_cycle():
    mixer = Mixer()
    test = mixer.cycle(3).blend(Test)
    assert len(test) == 3
    assert test[0].__class__ == Test

    test = mixer.cycle(3).blend(Test, name=mixer.sequence('lama{0}'))
    assert test[2].name == 'lama2'


def test_mixer_default():
    from mixer.main import mixer

    test = mixer.blend(Test)
    assert test.name


def test_invalid_scheme():
    from mixer.main import mixer

    with pytest.raises(ValueError):
        mixer.blend('tests.test_main.Unknown')


def test_sequence():
    from mixer.main import mixer

    gen = mixer.sequence()
    assert next(gen) == 0
    assert next(gen) == 1

    gen = mixer.sequence('test - {0}')
    assert next(gen) == 'test - 0'
    assert next(gen) == 'test - 1'

    gen = mixer.sequence(lambda c: c + 2)
    assert next(gen) == 2
    assert next(gen) == 3

    gen = mixer.sequence(4, 3)
    assert next(gen) == 4
    assert next(gen) == 3
    assert next(gen) == 4


def test_custom():
    mixer = Mixer()

    @mixer.middleware(Test)
    def postprocess(x): # noqa
        x.name += ' Done'
        return x

    mixer.register(
        Test,
        name='Mike',
        one=mixer.G.get_float,
        body=lambda: mixer.G.get_datetime((1980, 1, 1)),
    )

    test = mixer.blend(Test)
    assert test.name == 'Mike Done'
    assert isinstance(test.one, float)
    assert test.body >= datetime.datetime(1980, 1, 1)

    from mixer.main import GenFactory

    class MyFactory(GenFactory):
        generators = {str: lambda: "Always same"}

    mixer = Mixer(factory=MyFactory, fake=False)
    test = mixer.blend(Test)
    assert test.name == "Always same"


def test_ctx():
    from mixer.main import LOGGER

    mixer = Mixer()
    level = LOGGER.level

    with mixer.ctx(loglevel='INFO'):
        mixer.blend(Test)
        assert LOGGER.level != level

    assert LOGGER.level == level


def test_silence():
    mixer = Mixer()

    @mixer.middleware(Test)
    def falsed(test): # noqa
        raise Exception('Unhandled')

    with pytest.raises(Exception):
        mixer.blend(Test)

    with mixer.ctx(silence=True):
        mixer.blend(Test)


def test_guard():
    mixer = Mixer()
    test = mixer.guard().blend(Test)
    assert test


def test_skip():
    mixer = Mixer()
    test = mixer.blend(Test, one=mixer.SKIP)
    assert test.one is not mixer.SKIP
    assert test.one is int
