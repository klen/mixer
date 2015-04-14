import datetime as dt

import pytest
from peewee import *


db = SqliteDatabase(':memory:')


class Person(Model):
    name = CharField()
    created = DateTimeField(default=dt.datetime.now)
    birthday = DateField()
    is_relative = BooleanField()

    class Meta:
        database = db


class Pet(Model):
    owner = ForeignKeyField(Person, related_name='pets')
    name = CharField()
    animal_type = CharField()

    class Meta:
        database = db


Person.create_table()
Pet.create_table()


@pytest.fixture
def mixer():
    from mixer.backend.peewee import mixer
    return mixer


def test_mixer(mixer):
    person = mixer.blend(Person)
    assert person.name
    assert person.id
    assert person.birthday

    pet = mixer.blend(Pet)
    assert pet.name
    assert pet.animal_type
    assert pet.owner

    with mixer.ctx(commit=True):
        person = mixer.blend(Person)
        assert person.id == 1


def test_guard(mixer):
    person = mixer.blend(Person)
    person2 = mixer.guard(Person.name == person.name).blend(Person)
    assert person.id == person2.id


def test_reload(mixer):
    person = mixer.blend(Person, name='true')
    person.name = 'wrong'

    person = mixer.reload(person)
    person.name == 'true'
