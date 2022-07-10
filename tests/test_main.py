""" Test mixer base functionality. """
from __future__ import annotations
import datetime

import pytest
from decimal import Decimal

from mixer.main import Mixer, TypeMixer
from mixer.backend.annotated import (
    Mixer as AnnotationMixer,
    TypeMixer as AnnotationTypeMixer,
)


class Test:

    """Model scheme for base tests."""

    one = int
    two = int
    name = str
    title = str
    body = str
    price = Decimal
    choices = list
    parts = set
    scheme = dict


class AnnotationTest:
    one: int
    two: int
    name: str
    title: str
    body: str
    price: Decimal
    choices: list
    parts: set
    scheme: dict


class Scheme:
    id = int
    name = str
    money = int
    male = bool
    prop = Test


class AnnotationScheme:
    id: int
    name: str
    money: int
    male: bool
    prop: AnnotationTest


def test_factory():
    """Test base generator's factory."""
    from mixer.main import GenFactory

    g = GenFactory()
    test = g.get_fabric(int)
    assert -2147483647 <= test() < 2147483647

    test = g.get_fabric(bool)
    assert test() in (True, False)


@pytest.mark.parametrize(
    "typemixer_cls, scheme", [(TypeMixer, Test), (AnnotationTypeMixer, AnnotationTest)]
)
def test_typemixer_meta(typemixer_cls, scheme):
    """Tests that typemixer is a singleton for current class."""
    mixer1 = typemixer_cls(scheme)
    mixer2 = typemixer_cls(scheme, fake=False)
    mixer3 = typemixer_cls(scheme, fake=False)

    assert mixer1 is not mixer2
    assert mixer2 is mixer3


@pytest.mark.parametrize(
    "mixer", [TypeMixer(Scheme), AnnotationTypeMixer(AnnotationScheme)]
)
def test_typemixer(mixer):

    test = mixer.blend(prop__two=2, prop__one=1, prop__name="sigil", name="RJ")
    assert test.male in (True, False)
    assert test.name == "RJ"
    assert test.prop.two == 2
    assert test.prop.name == "sigil"

    test = mixer.blend(prop__two=4, unknown=lambda: "?")
    assert test.prop.two == 4
    assert test.unknown == "?"


@pytest.mark.parametrize(
    "mixer, scheme", [(Mixer(), Test), (AnnotationMixer(), AnnotationTest)]
)
def test_fake(mixer, scheme):

    test = mixer.blend(scheme, name=mixer.FAKE, title=mixer.FAKE)
    assert " " in test.name
    assert " " in test.title

    test = mixer.blend(scheme, name=mixer.FAKE(bool))
    assert test.name in (True, False)


@pytest.mark.parametrize("mixer", [TypeMixer(Test), AnnotationTypeMixer(Test)])
def test_random(mixer):
    from mixer._compat import string_types

    test = mixer.blend(name=mixer.RANDOM)
    assert isinstance(test.name, string_types)

    test = mixer.blend(name=mixer.RANDOM(int))
    assert isinstance(test.name, int)

    names = ["john_", "kenn_", "lenny_"]
    test = mixer.blend(name=mixer.RANDOM(*names))
    assert test.name in names


def test_mix():
    from mixer.main import mixer

    lama = type("One", tuple(), dict(two=int, one=type("Two", tuple(), dict(two=2.1))))
    mix = mixer.MIX.one.two
    assert mix & lama == 2.1

    test = mixer.blend(lama, one__two=2.1)
    assert test.one.two == 2.1
    assert test.two != test.one.two

    test = mixer.blend(lama, one__two=2.1, two=mixer.MIX.one.two)
    assert test.two == test.one.two


@pytest.mark.parametrize(
    "mixer, scheme", [(Mixer(), Test), (AnnotationMixer(), AnnotationTest)]
)
def test_mixer(mixer, scheme):

    assert Mixer.SKIP == mixer.SKIP
    try:
        Mixer.SKIP = 111
        raise AssertionError("test are failed")
    except AttributeError:
        pass
    try:
        mixer.SKIP = 111
        raise AssertionError("test are failed")
    except AttributeError:
        pass

    gen = ("test{0}".format(i) for i in range(500))
    test = mixer.blend(f"tests.test_main.{scheme.__name__}", name=gen)
    assert test.name == "test0"

    name_gen = mixer.sequence(lambda c: "test" + str(c))
    test = mixer.blend(scheme, name=name_gen)
    test = mixer.blend(scheme, name=name_gen)
    test = mixer.blend(scheme, name=name_gen)
    assert test.name == "test2"

    name_gen = mixer.sequence("test{0}")
    test = mixer.blend(scheme, name=name_gen)
    test = mixer.blend(scheme, name=name_gen)
    assert test.name == "test1"

    name_gen = mixer.sequence()
    test = mixer.blend(scheme, name=name_gen)
    test = mixer.blend(scheme, name=name_gen)
    assert test.name == 1

    mixer.register(
        f"tests.test_main.{scheme.__name__}",
        name="Michel",
        one=lambda: "ID",
        unknown="No error here",
    )
    test = mixer.blend(scheme)
    assert test.one == "ID"
    assert test.name == "Michel"


@pytest.mark.parametrize(
    "mixer, scheme", [(Mixer(), Test), (AnnotationMixer(), AnnotationTest)]
)
def test_mixer_cycle(mixer, scheme):
    test = mixer.cycle(3).blend(scheme)
    assert len(test) == 3
    assert test[0].__class__ == scheme

    test = mixer.cycle(3).blend(scheme, name=mixer.sequence("lama{0}"))
    assert test[2].name == "lama2"


@pytest.mark.parametrize(
    "mixer, scheme", [(Mixer(), Test), (AnnotationMixer(), AnnotationTest)]
)
def test_mixer_default(mixer, scheme):

    test = mixer.blend(scheme)
    assert test.name


@pytest.mark.parametrize("mixer", [Mixer(), AnnotationMixer()])
def test_invalid_scheme(mixer):

    with pytest.raises(ValueError):
        mixer.blend("tests.test_main.Unknown")


@pytest.mark.parametrize("mixer", [Mixer(), AnnotationMixer()])
def test_sequence(mixer):

    gen = mixer.sequence()
    assert next(gen) == 0
    assert next(gen) == 1

    gen = mixer.sequence("test - {0}")
    assert next(gen) == "test - 0"
    assert next(gen) == "test - 1"

    gen = mixer.sequence(lambda c: c + 2)
    assert next(gen) == 2
    assert next(gen) == 3

    gen = mixer.sequence(4, 3)
    assert next(gen) == 4
    assert next(gen) == 3
    assert next(gen) == 4


@pytest.mark.parametrize(
    "mixer_cls, scheme", [(Mixer, Test), (AnnotationMixer, AnnotationTest)]
)
def test_custom(mixer_cls, scheme):
    mixer = mixer_cls()
    @mixer.middleware(scheme)
    def postprocess(x):  # noqa
        x.name += " Done"
        return x

    mixer.register(
        scheme,
        name="Mike",
        one=mixer.faker.pyfloat,
        body=mixer.faker.date_time,
    )

    test = mixer.blend(scheme)
    assert test.name == "Mike Done"
    assert isinstance(test.one, float)
    assert isinstance(test.body, datetime.datetime)

    from mixer.main import GenFactory

    class MyFactory(GenFactory):
        generators = {str: lambda: "Always same"}

    mixer = mixer_cls(factory=MyFactory, fake=False)
    test = mixer.blend(scheme)
    assert test.name == "Always same"

@pytest.mark.parametrize(
    "mixer, scheme", [(Mixer(), Test), (AnnotationMixer(), AnnotationTest)]
)
def test_ctx(mixer,scheme):
    from mixer.main import LOGGER

    
    level = LOGGER.level

    with mixer.ctx(loglevel="INFO"):
        mixer.blend(scheme)
        assert LOGGER.level != level

    dw = mixer.faker.day_of_week()
    assert dw[0] in "MTWFS"

    with mixer.ctx(locale="ru"):
        dw = mixer.faker.day_of_week()
        assert dw[0] in "ПВСЧ"

    assert LOGGER.level == level

@pytest.mark.parametrize(
    "mixer", [Mixer(), AnnotationMixer()]
)
def test_locale(mixer):
    mixer.faker.locale = "ru"

    with mixer.ctx(locale="it"):
        mixer.faker.name()

    assert mixer.faker.locale == "ru_RU"

    with mixer.ctx(loglevel="INFO"):
        mixer.faker.name()

    assert mixer.faker.locale == "ru_RU"

@pytest.mark.parametrize(
    "mixer, scheme", [(Mixer(), Test), (AnnotationMixer(), AnnotationTest)]
)
def test_silence(mixer, scheme):
    

    class CustomException(Exception):
        pass

    @mixer.middleware(scheme)
    def falsed(test):  # noqa
        raise CustomException("Unhandled")

    with pytest.raises(CustomException):
        mixer.blend(scheme)

    with mixer.ctx(silence=True):
        mixer.blend(scheme)

    mixer.unregister_middleware(scheme, falsed)
    mixer.blend(scheme)  # does not raise any exceptions

@pytest.mark.parametrize(
    "mixer, scheme", [(Mixer(), Test), (AnnotationMixer(), AnnotationTest)]
)
def test_guard(mixer, scheme):
    test = mixer.guard().blend(scheme)
    assert test


def test_skip():
    mixer = Mixer()
    test = mixer.blend(Test, one=mixer.SKIP)
    assert test.one is not mixer.SKIP
    assert test.one is int

@pytest.mark.parametrize(
    "mixer, scheme", [(Mixer(), Test), (AnnotationMixer(), AnnotationTest)]
)
def test_reload(mixer, scheme):
    test = mixer.blend(scheme)
    test2 = mixer.reload(test)
    assert test is not test2
    assert test.name == test2.name

    test3, test4 = mixer.reload(test, test2)
    assert test3 and test4
