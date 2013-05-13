from __future__ import absolute_import

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
    ForeignKey,
)
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base
from unittest import TestCase


ENGINE = create_engine('sqlite:///:memory:')
BASE = declarative_base()


class User(BASE):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)
    role = Column(String(10), default='client', nullable=False)
    updated = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Role(BASE):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    user = relation(User)


class MixerTestSQLAlchemy(TestCase):

    def test_backend(self):
        from mixer.backends.sqlalchemy import TypeMixer

        mixer = TypeMixer(User)
        user = mixer.blend()
        self.assertTrue(user)
        self.assertTrue(user.id)
        self.assertTrue(user.name)
        self.assertEqual(len(user.name), 10)
        self.assertEqual(user.role, 'client')
        self.assertTrue(user.updated is None)

        user = mixer.blend(name='John', updated=mixer.random)
        self.assertEqual(user.name, 'John')
        self.assertTrue(user.updated in (True, False))

        # mixer = TypeMixer('tests.sqlalchemy.Role')
        # role = mixer.blend()
        # self.assertTrue(role.user)
        # self.assertEqual(role.user_id, role.user.id)
