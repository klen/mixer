from __future__ import absolute_import

from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

usermessages = db.Table(
    'users_usermessages',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('message_id', db.Integer, db.ForeignKey('message.id'))
)


class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    user = db.relationship("User", uselist=False, backref="profile")


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.SmallInteger, default=50, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    username = db.Column(db.String(20), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profile.id'), nullable=False)

    messages = db.relationship("Message", secondary=usermessages, backref="users")


class Role(db.Model):

    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    user = db.relation(User)


class Message(db.Model):

    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(20))


class Node(db.Model):

    __tablename__ = 'node'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    children = db.relation(
        'Node',
        cascade='all',
        backref=db.backref('parent', remote_side='Node.id'))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db.init_app(app)


def test_base():
    from mixer.backend.flask import Mixer

    mixer = Mixer(commit=True)
    mixer.init_app(app)

    with app.test_request_context():
        db.create_all()

        node = mixer.blend('tests.test_flask.Node')
        assert node.id
        assert not node.parent

        role = mixer.blend('tests.test_flask.Role')
        assert role.user
        assert role.user_id == role.user.id

        user = mixer.blend(User)
        assert user.id
        assert user.username
        assert user.score == 50
        assert user.created_at
        assert user.profile
        assert user.profile.user == user

        user = mixer.blend(User, username='test')
        assert user.username == 'test'

        role = mixer.blend('tests.test_flask.Role', user__username='test2')
        assert role.user.username == 'test2'

        users = User.query.all()
        role = mixer.blend('tests.test_flask.Role', user=mixer.SELECT)
        assert role.user in users

        role = mixer.blend('tests.test_flask.Role', user=mixer.RANDOM)
        assert role.user

        profile = mixer.blend('tests.test_flask.Profile')
        user = mixer.blend(User, profile=profile)
        assert user.profile == profile

        user = mixer.blend(User, score=mixer.RANDOM)
        assert user.score != 50

        user = mixer.blend(User, username=lambda: 'callable_value')
        assert user.username == 'callable_value'

        # m2m
        messages = mixer.cycle(3).blend(Message)
        user = mixer.blend(User, messages=messages)
        assert len(user.messages) == 3

        user = mixer.blend(User, messages=mixer.RANDOM)
        assert len(user.messages) == 1

        user = mixer.blend(User, messages__content='message_content')
        assert len(user.messages) == 1
        assert user.messages[0].content == 'message_content'


def test_default_mixer():
    from mixer.backend.flask import mixer

    test = mixer.blend(User)
    assert test.username

# lint_ignore=F0401
