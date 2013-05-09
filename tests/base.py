from unittest import TestCase


class MixerBaseTests(TestCase):

    def test_base(self):
        from mixer import __version__
        self.assertTrue(__version__)

    def test_generators(self):
        from mixer import generators as g

        test = next(g.gen_choice(1, 2, 3))
        self.assertTrue(test in (1, 2, 3))

        self.assertTrue(g.get_date())

        test = next(g.gen_time())
        self.assertTrue(test)

        test = next(g.gen_datetime())
        self.assertTrue(test)

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
        from mixer import fakers as f

        test = next(f.gen_name())
        self.assertTrue(test)

        test = next(f.gen_city())
        self.assertTrue(test)

        test = next(f.gen_lorem(length=30))
        self.assertEqual(len(test), 30)

        test = next(f.gen_numerify('##-####'))
        self.assertTrue(test)

    def test_generatorregistry(self):
        from mixer.main import GeneratorRegistry

        g = GeneratorRegistry()
        test = g.random(int)
        self.assertTrue(-2147483647 <= test < 2147483647)

        test = g.random(bool)
        self.assertTrue(test in [True, False])

    def test_mixer(self):
        from mixer.main import TypeMixer

        class Scheme:
            name = str
            money = int
            male = bool

        mixer = TypeMixer(Scheme)
        test = mixer.blend()
        self.assertTrue(test.male in [True, False])
        self.assertTrue(len(test.name))

        test = mixer.blend(name='John')
        self.assertEqual(test.name, 'John')

        test = mixer.blend(name=mixer.fake)
        self.assertTrue(' ' in test.name)
