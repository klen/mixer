from peewee import *


db = SqliteDatabase(':memory:')


class Person(Model):
    name = CharField()
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


def test_backend():
    from mixer.backend.peewee import mixer
    assert mixer


def test_mixer():
    from mixer.backend.peewee import mixer

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
