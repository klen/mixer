from __future__ import absolute_import

from datetime import datetime
from random import randrange

import pytest
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    create_engine,
    types
)
from sqlalchemy.dialects import mssql, mysql, oracle, postgresql, sqlite
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, relationship, scoped_session, sessionmaker
from sqlalchemy.util import text_type

ENGINE = create_engine('sqlite:///:memory:')
BASE = declarative_base()
SESSION = scoped_session(sessionmaker(bind=ENGINE))


class Profile(BASE):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)

    user = relationship("User", uselist=False, backref="profile")


class ProfileNonIncremental(BASE):
    __tablename__ = 'profile_nonincremental'

    id = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    name = Column(String(20), nullable=False)

    user = relationship("User", uselist=False, backref="profile_nonincremental")


class AugmentedType(types.TypeDecorator):
    impl = String


class User(BASE):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)
    role = Column(String(10), default='client', nullable=False)
    score = Column(SmallInteger, name='points', default=50, nullable=False)
    updated_at = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    enum = Column(Enum('one', 'two'), nullable=False)
    random = Column(Integer, default=lambda: randrange(993, 995))
    profile_id = Column(Integer, ForeignKey('profile.id'), nullable=False)
    profile_id_nonincremental = Column(
        Integer, ForeignKey('profile_nonincremental.id'), nullable=False)
    augmented = Column(AugmentedType, default='augmented', nullable=False)


class Role(BASE):
    __tablename__ = 'role'

    name = Column(String(20), primary_key=True)
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
    assert 993 <= user.random < 995
    assert user.score == 50
    assert 2 < len(user.name) <= 10
    assert user.role == 'client'
    assert user.updated_at is None
    assert user.profile
    assert user.profile.user == user
    assert user.enum in ('one', 'two')
    assert user.augmented == 'augmented'

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
    p = mixer.blend('tests.test_sqlalchemy.ProfileNonIncremental', id=5)
    role = mixer.blend('tests.test_sqlalchemy.Role', user__profile_id_nonincremental=p)
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


def test_cycle(session):
    from mixer.backend.sqlalchemy import Mixer

    mixer = Mixer(session=session, commit=True)
    profile1 = mixer.blend('tests.test_sqlalchemy.Profile', name='first')
    profile2 = mixer.blend('tests.test_sqlalchemy.Profile', name='second')
    users = mixer.cycle(2).blend(User, profile=(p for p in (profile1, profile2)))
    assert len(users) == 2
    assert users[0].profile.name == 'first'
    assert users[1].profile.name == 'second'


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


def test_guard(session):
    from mixer.backend.sqlalchemy import Mixer, mixer

    with pytest.raises(ValueError):
        mixer.guard(User.name == 'maxi').blend(User)

    mixer = Mixer(session=session, commit=True)

    u1 = mixer.guard(User.name == 'maxi').blend(User, name='maxi')
    u2 = mixer.guard(User.name == 'maxi').blend(User)
    assert u1
    assert u1 == u2


def test_reload(session):
    from mixer.backend.sqlalchemy import Mixer

    mixer = Mixer(session=session, commit=True)

    u1 = mixer.blend(User)
    u1.name = 'wrong name'
    u2 = mixer.reload(u1)
    assert u2 == u1
    assert u2.name != 'wrong name'


def test_mix22(session):
    from mixer.backend.sqlalchemy import Mixer

    mixer = Mixer(session=session, commit=True)
    role = mixer.blend(Role, name=mixer.MIX.user.name)
    assert role.name == role.user.name


def test_nonincremental_primary_key(session):
    from mixer.backend.sqlalchemy import mixer

    test = mixer.blend(ProfileNonIncremental, id=42)
    assert test.name


def test_postgresql():
    from mixer.backend.sqlalchemy import TypeMixer
    from sqlalchemy.dialects.postgresql import UUID

    base = declarative_base()

    class Test(base):
        __tablename__ = 'test'

        id = Column(Integer, primary_key=True)
        uuid = Column(UUID, nullable=False)

    mixer = TypeMixer(Test)
    test = mixer.blend()
    assert test.uuid


@pytest.mark.parametrize('dialect, expected', [
    (mssql.dialect(), 'RAND()'),
    (mysql.dialect(), 'RAND()'),
    (oracle.dialect(), 'DBMS_RANDOM.VALUE'),
    (postgresql.dialect(), 'RANDOM()'),
    (sqlite.dialect(), 'RANDOM()'),
])
def test_random_compiled(dialect, expected):
    from mixer.backend.sqlalchemy import random
    compiled = random().compile(dialect=dialect)
    assert text_type(compiled) == expected
