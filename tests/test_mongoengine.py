from __future__ import absolute_import
from mongoengine import *
import datetime
try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase


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


class MixerTestMongoEngine(TestCase):

    def test_base(self):
        from mixer.backend.mongoengine import mixer

        self.assertTrue(mixer)

        user = mixer.blend(User)
        self.assertTrue(user.id)

    def test_generators(self):
        from mixer.backend.mongoengine import get_polygon

        polygon = get_polygon()
        self.assertTrue(polygon['coordinates'])

    def test_typemixer(self):
        from mixer.backend.mongoengine import TypeMixer

        now = datetime.datetime.now()

        tm = TypeMixer(User)
        user = tm.blend()
        self.assertTrue(user.id)
        self.assertTrue(user.email)
        self.assertTrue(user.created_at)
        self.assertTrue(user.created_at >= now)

        tm = TypeMixer(Post)
        post = tm.blend(comments=tm.random, place=tm.random)
        self.assertTrue(post.id)
        self.assertTrue(post.title)
        self.assertEqual(post.tags, [])
        self.assertTrue(post.comments)
        self.assertTrue(post.comments[0])
        self.assertTrue(isinstance(post.comments[0], Comment))
        self.assertTrue(post.author)
        self.assertTrue(post.author.email)
        self.assertTrue(post.rating)
        self.assertTrue(post.category in ('S', 'M'))
        self.assertTrue('/' in post.url)
        self.assertTrue('-' in post.uuid)
        self.assertTrue('coordinates' in post.place)

    def test_relation(self):
        from mixer.backend.mongoengine import mixer

        post = mixer.blend(
            'tests.test_mongoengine.Post', author__username='foo')
        self.assertEqual(post.author.username, 'foo')

        bookmark = mixer.blend(Bookmark)
        self.assertTrue(bookmark.bookmark)


# lint_ignore=C,W0614,W0401,R0924,F0401
