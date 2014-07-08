from __future__ import absolute_import

import sys

import pytest


pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 0), reason="requires python3")


def test_base():
    from yadm import Document, fields

    class Author(Document):

        name = fields.StringField()

    class Place(Document):

        address = fields.StringField()

    class BlogPost(Document):

        title = fields.StringField()
        body = fields.StringField()
        tags = fields.ListField(fields.StringField)
        place = fields.EmbeddedDocumentField(Place)

        author = fields.ReferenceField(Author)

    from mixer.backend.yadm import mixer
    assert mixer

    post = mixer.blend(BlogPost, tags=mixer.RANDOM, author__name="Tomas")
    assert post.title
    assert post.body
    assert post.tags
    assert post.author.name == 'Tomas'


# pylama:ignore=D,F0401
