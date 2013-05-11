from __future__ import absolute_import

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from unittest import TestCase


ENGINE = create_engine('sqlite:///:memory:')
BASE = declarative_base()


class User(BASE):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(10))


class MixerTestSQLAlchemy(TestCase):

    def test_backend(self):
        from mixer.backends.sqlalchemy import TypeMixer

        mixer = TypeMixer(User)
        user = mixer.blend()
        self.assertTrue(user)
        self.assertTrue(user.id)
        self.assertTrue(user.name)

        user = mixer.blend(name='John')
        self.assertEqual(user.name, 'John')
