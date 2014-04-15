from __future__ import absolute_import
from mongoengine import *
import datetime


class User(Document):
    created_at = DateTimeField(default=datetime.datetime.now)
    email = EmailField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)


class Comment(EmbeddedDocument):
    content = StringField()
    name = StringField(max_length=120)


class Post(Document):
    title = StringField(max_length=120, required=True)
    author = ReferenceField(User)
    category = StringField(choices=(
        ('S', 'Super'), ('M', 'Medium')), required=True)
    size = StringField(
        max_length=3, choices=('S', 'M', 'L', 'XL', 'XXL'), required=True)
    tags = ListField(StringField(max_length=30))
    comments = ListField(EmbeddedDocumentField(Comment))
    rating = DecimalField(precision=4, required=True)
    url = URLField(required=True)
    uuid = UUIDField(required=True)
    place = PointField()

    meta = {'allow_inheritance': True}


class Bookmark(Document):
    user = ReferenceField(User)
    bookmark = GenericReferenceField()


def test_generators():
    from mixer.backend.mongoengine import get_polygon

    polygon = get_polygon()
    assert polygon['coordinates']


def test_base():
    from mixer.backend.mongoengine import Mixer

    mixer = Mixer(commit=False)
    assert mixer

    now = datetime.datetime.now()

    user = mixer.blend(User)
    assert user.id
    assert user.email
    assert user.created_at
    assert user.created_at >= now


def test_typemixer():
    from mixer.backend.mongoengine import TypeMixer

    tm = TypeMixer(Post)
    post = tm.blend(comments=tm.RANDOM, place=tm.RANDOM)
    assert post.id
    assert post.title
    assert post.tags == []
    assert post.comments
    assert post.comments[0]
    assert isinstance(post.comments[0], Comment)
    assert post.author
    assert post.author.email
    assert post.rating
    assert post.category in ('S', 'M')
    assert '/' in post.url
    assert '-' in post.uuid
    assert 'coordinates' in post.place


def test_relation():
    from mixer.backend.mongoengine import Mixer

    mixer = Mixer(commit=False)

    post = mixer.blend(
        'tests.test_mongoengine.Post', author__username='foo')
    assert post.author.username == 'foo'

    bookmark = mixer.blend(Bookmark)
    assert not bookmark.bookmark

    bookmark = mixer.blend(Bookmark, bookmark=mixer.RANDOM)
    assert bookmark.bookmark


# pylama:ignore=W0401,W0614
