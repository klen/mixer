import marshmallow as ma
import pytest


class Person(ma.Schema):

    name = ma.fields.String()
    status = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf(choices=('user', 'moderator', 'admin')))
    created = ma.fields.DateTime()
    birthday = ma.fields.Date()
    is_relative = ma.fields.Bool()


class Pet(ma.Schema):

    name = ma.fields.String()
    animal_type = ma.fields.String(default='cat')
    owner = ma.fields.Nested(Person, many=True)
    awards = ma.fields.List(ma.fields.Str)


@pytest.fixture
def mixer():
    from mixer.backend.marshmallow import Mixer
    return Mixer(required=True)


def test_mixer(mixer):
    person = mixer.blend(Person)
    assert person['name']
    assert person['birthday']
    assert person['created']
    assert isinstance(person['is_relative'], bool)
    assert person['status'] in ('user', 'moderator', 'admin')

    pet = mixer.blend(Pet)
    assert pet['name']
    assert pet['animal_type'] == 'cat'
    assert pet['owner']
    assert pet['awards'] is not None
