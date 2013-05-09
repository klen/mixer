from __future__ import absolute_import

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from unittest import TestCase


ENGINE = create_engine('sqlite:///:memory:')
BASE = declarative_base()


class User(BASE):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class MixerTestSQLAlchemy(TestCase):

    def test_backend(self):
        from mixer.backends.sqlalchemy import TypeMixer

        mixer = TypeMixer(User)
        user = mixer.blend()
        import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
        self.assertTrue(user)
