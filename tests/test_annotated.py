from __future__ import annotations
import typing as t
import typing_extensions as te
from mixer.backend.annotated import Mixer
from dataclasses import dataclass


class Test:
    one: int
    two: int
    name: str
    title: str
    body: str
    price: t.Optional[int]
    something: t.Union[int, str]
    choices: list
    parts: set
    scheme: dict


def test_factory():
    from mixer.backend.annotated import GenFactory

    g = GenFactory()
    test = g.get_fabric(t.Optional[int])
    assert isinstance(test(), (int, type(None)))

    test = g.get_fabric(t.Union[str, int])
    assert isinstance(test(), (str, int))


def test_annotated():
    mixer = Mixer()
    test = mixer.blend(Test)
    assert isinstance(test.price, (int, type(None)))
    assert isinstance(test.something, (int, str))


def test_typed_dict():
    class TestDict(te.TypedDict):
        one: int
        two: int
        name: str

    mixer = Mixer()
    test = mixer.blend(TestDict)

    assert isinstance(test, dict)
    assert "one" in test and "two" in test and "name" in test
    assert isinstance(test["one"], int) and isinstance(test["two"], int) and isinstance(test["name"], str)


def test_dataclass():
    @dataclass
    class TestDataclass:
        one: int
        two: int
        name: str

    mixer = Mixer()
    test = mixer.blend(TestDataclass)

    assert isinstance(test, TestDataclass)
    assert isinstance(test.one, int) and isinstance(test.two, int) and isinstance(test.name, str)
