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
    Enum,
)
from sqlalchemy.orm import relation, sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import pytest


ENGINE = create_engine('sqlite:///:memory:')
BASE = declarative_base()
SESSION = scoped_session(sessionmaker(bind=ENGINE))


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
    enum = Column(Enum('one', 'two'), nullable=False)

    profile_id = Column(Integer, ForeignKey('profile.id'), nullable=False)


class Role(BASE):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    user = relation(User)


BASE.metadata.create_all(ENGINE)


@pytest.fixture
def session():
    return SESSION()


def test_typemixer():
    from mixer.backend.sqlalchemy import TypeMixer

    mixer = TypeMixer(User)
    user = mixer.blend()
    assert user
    assert not user.id
    assert user.name
    assert user.score == 50
    assert 2 < len(user.name) <= 10
    assert user.role == 'client'
    assert user.updated_at is None
    assert user.profile
    assert user.profile.user == user
    assert user.enum in ('one', 'two')

    user = mixer.blend(name='John', updated_at=mixer.RANDOM)
    assert user.name == 'John'
    assert user.updated_at in (True, False)

    mixer = TypeMixer('tests.test_sqlalchemy.Role')
    role = mixer.blend()
    assert role.user
    assert role.user_id == role.user.id


def test_mixer(session):
    from mixer.backend.sqlalchemy import Mixer

    mixer = Mixer(session=session, commit=True)
    role = mixer.blend('tests.test_sqlalchemy.Role')
    assert role and role.user

    role = mixer.blend(Role, user__name='test2')
    assert role.user.name == 'test2'

    profile = mixer.blend('tests.test_sqlalchemy.Profile')
    user = mixer.blend(User, profile__name='test')
    assert user.profile.name == 'test'

    user = mixer.blend(User, profile=profile)
    assert user.profile == profile

    user = mixer.blend(User, score=mixer.RANDOM)
    assert user.score != 50

    user = mixer.blend(User, username=lambda: 'callable_value')
    assert user.username == 'callable_value'


def test_select(session):
    from mixer.backend.sqlalchemy import Mixer

    mixer = Mixer(session=session, commit=True)

    users = session.query(User).all()
    role = mixer.blend(Role, user=mixer.SELECT)
    assert role.user in users

    user = users.pop()
    role = mixer.blend(Role, user=mixer.SELECT(User.id == user.id))
    assert user == role.user


def test_random():
    from mixer.backend.sqlalchemy import mixer

    values = ('mixer', 'is', 'fun')
    user = mixer.blend(User, name=mixer.RANDOM(*values))
    assert user.name in values


def test_default_mixer():
    from mixer.backend.sqlalchemy import mixer

    test = mixer.blend(User)
    assert test.name
