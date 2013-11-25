""" Test mixer base functionality. """
import datetime

from mixer.main import Mixer
from decimal import Decimal


try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase


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


class MixerBaseTests(TestCase):

    """ Test base mixer classes. """

    def test_base(self):
        """ Just import version. """
        from mixer import __version__
        self.assertTrue(__version__)

    def test_generators(self):
        """ Test random generators. """
        from mixer import generators as g

        test = next(g.gen_choice((1, 2, 3)))
        self.assertTrue(test in (1, 2, 3))

        test = next(g.gen_date())
        self.assertTrue(isinstance(test, datetime.date))

        min_date, max_date = (2010, 1, 1), (2011, 1, 1)
        test = next(g.gen_date(min_date, max_date))
        self.assertTrue(2010 <= test.year <= 2011)

        test = next(g.gen_date(
            datetime.date(*min_date), datetime.date(*max_date)))
        self.assertTrue(2010 <= test.year <= 2011)

        test = next(g.gen_time())
        self.assertTrue(isinstance(test, datetime.time))

        min_time, max_time = (14, 30), (15, 30)
        test = next(g.gen_time(min_time, max_time))
        self.assertTrue(14 <= test.hour <= 15)

        test = next(g.gen_time(
            datetime.time(*min_time), datetime.time(*max_time)))
        self.assertTrue(14 <= test.hour <= 15)

        test = next(g.gen_datetime())
        self.assertTrue(isinstance(test, datetime.datetime))

        test = next(g.gen_integer())
        self.assertTrue(-2147483647 <= test < 2147483647)

        test = next(g.gen_big_integer())
        self.assertTrue(-9223372036854775808 <= test < 9223372036854775808)

        test = next(g.gen_small_integer())
        self.assertTrue(-32768 <= test < 32768)

        test = next(g.gen_positive_integer())
        self.assertTrue(test >= 0)

        test = next(g.gen_small_positive_integer())
        self.assertTrue(test >= 0)

        test = next(g.gen_float())
        self.assertTrue(test)

        test = next(g.gen_boolean())
        self.assertTrue(test in (True, False))

        test = next(g.gen_string())
        self.assertTrue(test)

        test = next(g.gen_decimal())
        self.assertTrue(test)

        test = next(g.gen_positive_decimal())
        self.assertTrue(test)

    def test_faker(self):
        """ Test default fakers. """
        from mixer import fakers as f

        test = next(f.gen_name())
        self.assertTrue(test)

        test = next(f.gen_city())
        self.assertTrue(test)

        test = next(f.gen_lorem(length=30))
        self.assertEqual(len(test), 30)

        test = next(f.gen_numerify('##-####'))
        self.assertTrue(test)

        test = next(f.gen_username(length=50))
        self.assertTrue(test)

        test = next(f.gen_simple_username(length=50))
        self.assertTrue(test)

        test = next(f.gen_hostname())
        self.assertTrue(test)

        test = next(f.gen_email())
        self.assertTrue(test)

        test = next(f.gen_email(host='gmail'))
        self.assertTrue('gmail' in test)

        test = next(f.gen_ip4())
        self.assertTrue('.' in test)

        test = next(f.gen_url())
        self.assertTrue('/' in test)

        test = next(f.gen_uuid())
        self.assertTrue('-' in test)

        test = next(f.gen_phone())
        self.assertTrue('-' in test)

        test = next(f.gen_company())
        self.assertTrue(test)

        test = next(f.gen_latlon())
        self.assertTrue(test)

        test = next(f.gen_coordinates())
        self.assertTrue(test)

    def test_factory(self):
        """ Test base generator's factory. """
        from mixer.main import GenFactory

        g = GenFactory()
        test = g.gen_maker(int)()
        self.assertTrue(-2147483647 <= next(test) < 2147483647)

        test = g.gen_maker(bool)()
        self.assertTrue(next(test) in [True, False])

    def test_typemixer_meta(self):
        """ Tests that typemixer is a singleton for current class. """
        from mixer.main import TypeMixer

        mixer1 = TypeMixer(Test)
        mixer2 = TypeMixer(Test, fake=False)
        mixer3 = TypeMixer(Test, fake=False)
        self.assertNotEqual(mixer1, mixer2)
        self.assertEqual(mixer2, mixer3)

    def test_typemixer(self):
        from mixer.main import TypeMixer

        class Scheme:
            id = int
            name = str
            money = int
            male = bool
            prop = Test

        mixer = TypeMixer(Scheme)
        test = mixer.blend(prop__two=2, prop__one=1, prop__name='sigil')
        self.assertTrue(test.male in [True, False])
        self.assertEqual(test.prop.two, 2)
        self.assertEqual(test.prop.name, 'sigil')

        test = mixer.blend(name='John')
        self.assertEqual(test.name, 'John')

        mixer.register('name', lambda: 'Piter')
        test = mixer.blend()
        self.assertEqual(test.name, 'Piter')

    def test_fake(self):
        from mixer.main import mixer

        test = mixer.blend(Test, name=mixer.fake, title=mixer.fake)
        self.assertTrue(' ' in test.name)
        self.assertTrue(' ' in test.title)

        test = mixer.blend(Test, name=mixer.fake(bool))
        self.assertTrue(test.name in (True, False))

    def test_random(self):
        from mixer.main import TypeMixer
        from mixer.six import string_types

        mixer = TypeMixer(Test)
        test = mixer.blend(name=mixer.random)
        self.assertTrue(isinstance(test.name, string_types))
        self.assertFalse(' ' in test.name)

        test = mixer.blend(name=mixer.random(int))
        self.assertTrue(isinstance(test.name, int))

        names = ['john_', 'kenn_', 'lenny_']
        test = mixer.blend(name=mixer.random(*names))
        self.assertTrue(test.name in names)

    def test_mix(self):
        from mixer.main import mixer
        lama = type('One', tuple(), dict(
            two=int,
            one=type('Two', tuple(), dict(two=2.1))
        ))
        mix = mixer.mix.one.two
        self.assertEqual(mix & lama, 2.1)

        test = mixer.blend(lama, one__two=2.1)
        self.assertEqual(test.one.two, 2.1)
        self.assertNotEqual(test.two, test.one.two)

        test = mixer.blend(lama, one__two=2.1, two=mixer.mix.one.two)
        self.assertEqual(test.two, test.one.two)

    def test_mixer(self):
        mixer = Mixer()

        gen = ('test{0}'.format(i) for i in range(500))
        test = mixer.blend('tests.test_main.Test', name=gen)
        self.assertEqual(test.name, 'test0')

        name_gen = mixer.sequence(lambda c: 'test' + str(c))
        test = mixer.blend(Test, name=name_gen)
        test = mixer.blend(Test, name=name_gen)
        test = mixer.blend(Test, name=name_gen)
        self.assertEqual(test.name, 'test2')

        name_gen = mixer.sequence('test{0}')
        test = mixer.blend(Test, name=name_gen)
        test = mixer.blend(Test, name=name_gen)
        self.assertEqual(test.name, 'test1')

        name_gen = mixer.sequence()
        test = mixer.blend(Test, name=name_gen)
        test = mixer.blend(Test, name=name_gen)
        self.assertEqual(test.name, 1)

        mixer.register('tests.test_main.Test', dict(
            name='Michel',
            one=lambda: 'ID',
            unknown="No error here"
        ))
        test = mixer.blend(Test)
        self.assertEqual(test.one, 'ID')
        self.assertEqual(test.name, 'Michel')

    def test_mixer_cycle(self):
        mixer = Mixer()
        test = mixer.cycle(3).blend(Test)
        self.assertEqual(len(test), 3)
        self.assertTrue(type(test[0]), Test)

        test = mixer.cycle(3).blend(Test,
                                    name=mixer.sequence('lama{0}'))
        self.assertEqual(test[2].name, 'lama2')

    def test_mixer_default(self):
        from mixer.main import mixer

        test = mixer.blend(Test)
        self.assertTrue(test.name)

    @staticmethod
    def test_invalid_scheme():
        from mixer.main import mixer
        try:
            mixer.blend('tests.test_main.Unknown')
        except ValueError:
            return False
        raise Exception('test.failed')

    def test_sequence(self):
        from mixer.main import mixer

        gen = mixer.sequence()
        self.assertEqual(next(gen), 0)
        self.assertEqual(next(gen), 1)

        gen = mixer.sequence('test - {0}')
        self.assertEqual(next(gen), 'test - 0')
        self.assertEqual(next(gen), 'test - 1')

        gen = mixer.sequence(lambda c: c + 2)
        self.assertEqual(next(gen), 2)
        self.assertEqual(next(gen), 3)

        gen = mixer.sequence(4, 3)
        self.assertEqual(next(gen), 4)
        self.assertEqual(next(gen), 3)
        self.assertEqual(next(gen), 4)

    def test_custom(self):
        mixer = Mixer()

        def postprocess(x):
            x.name += ' Done'
            return x

        mixer.register(Test, {
            'name': 'Mike',
            'one': mixer.g.get_float,
            'body': lambda: mixer.g.get_datetime((1980, 1, 1)),
        }, postprocess=postprocess)

        test = mixer.blend(Test)
        self.assertEqual(test.name, 'Mike Done')
        self.assertTrue(isinstance(test.one, float))
        self.assertTrue(test.body >= datetime.datetime(1980, 1, 1))

        from mixer.main import GenFactory

        class MyFactory(GenFactory):
            generators = {str: lambda: "Always same"}

        mixer = Mixer(factory=MyFactory, fake=False)
        test = mixer.blend(Test)
        self.assertEqual(test.name, "Always same")
