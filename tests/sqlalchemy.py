from __future__ import absolute_import

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    SmallInteger,
    String,
    create_engine,
    ForeignKey,
)
from sqlalchemy.orm import relation, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from unittest import TestCase


ENGINE = create_engine('sqlite:///:memory:')
BASE = declarative_base()
SESSION = sessionmaker(bind=ENGINE)


class Profile(BASE):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)

    user = relationship("User", uselist=False, backref="profile")


class User(BASE):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)
    role = Column(String(10), default='client', nullable=False)
    score = Column(SmallInteger, default=50, nullable=False)
    updated_at = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profile_id = Column(Integer, ForeignKey('profile.id'), nullable=False)


class Role(BASE):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    user = relation(User)


BASE.metadata.create_all(ENGINE)


class MixerTestSQLAlchemy(TestCase):

    def setUp(self):
        self.session = SESSION()

    def test_typemixer(self):
        from mixer.backend.sqlalchemy import TypeMixer

        mixer = TypeMixer(User)
        user = mixer.blend()
        self.assertTrue(user)
        self.assertFalse(user.id)
        self.assertTrue(user.name)
        self.assertEqual(user.score, 50)
        self.assertEqual(len(user.name), 10)
        self.assertEqual(user.role, 'client')
        self.assertTrue(user.updated_at is None)
        self.assertTrue(user.profile)
        self.assertEqual(user.profile.user, user)

        user = mixer.blend(name='John', updated_at=mixer.random)
        self.assertEqual(user.name, 'John')
        self.assertTrue(user.updated_at in (True, False))

        mixer = TypeMixer('tests.sqlalchemy.Role')
        role = mixer.blend()
        self.assertTrue(role.user)
        self.assertEqual(role.user_id, role.user.id)

    def test_mixer(self):
        from mixer.backend.sqlalchemy import Mixer

        mixer = Mixer(session=self.session, commit=True)
        role = mixer.blend('tests.sqlalchemy.Role')
        self.assertTrue(role)
        self.assertTrue(role.user)

        role = mixer.blend(Role, user__name='test2')
        self.assertEqual(role.user.name, 'test2')

        users = self.session.query(User).all()
        role = mixer.blend(Role, user=mixer.select)
        self.assertTrue(role.user in users)

        profile = mixer.blend('tests.sqlalchemy.Profile')
        user = mixer.blend(User, profile__name='test')
        self.assertEqual(user.profile.name, 'test')

        # user = mixer.blend(User, profile=profile)
        # self.assertEqual(user.profile, profile)

        user = mixer.blend(User, score=mixer.random)
        self.assertNotEqual(user.score, 50)

        user = mixer.blend(User, username=lambda: 'callable_value')
        self.assertEqual(user.username, 'callable_value')
