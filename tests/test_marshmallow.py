import marshmallow as ma
import pytest


class Person(ma.Schema):

    name = ma.fields.String(required=True)
    status = ma.fields.String(
        required=True,
        validate=ma.validate.OneOf(choices=('user', 'moderator', 'admin')))
    created = ma.fields.DateTime(required=True)
    birthday = ma.fields.Date(required=True)
    is_relative = ma.fields.Bool(required=True)


class Pet(ma.Schema):

    name = ma.fields.String(required=True)
    animal_type = ma.fields.String(default='cat')
    owner = ma.fields.Nested(Person, required=True, many=True)
    awards = ma.fields.List(ma.fields.Str, required=True)


@pytest.fixture
def mixer():
    from mixer.backend.marshmallow import mixer
    return mixer


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
    assert pet['awards']
