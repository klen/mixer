from __future__ import absolute_import

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           nullable=False)
    username = db.Column(db.String(20), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profile.id'), nullable=False)

    messages = db.relationship(
        "Message", secondary=usermessages, backref="users")


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    user = db.relation(User)


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)


class Node(db.Model):
    __tablename__ = 'node'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    children = db.relation(
        'Node',
        cascade='all',
        backref=db.backref('parent', remote_side='Node.id'))


class MixerTestFlask(TestCase):

    def setUp(self):
        from flask import Flask

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(self.app)

    def test_base(self):
        from mixer.backend.flask import Mixer

        mixer = Mixer(commit=True)
        mixer.init_app(self.app)

        with self.app.test_request_context():
            db.create_all()

            node = mixer.blend('tests.test_flask.Node')
            self.assertTrue(node.id)
            self.assertFalse(node.parent)

            role = mixer.blend('tests.test_flask.Role')
            self.assertTrue(role.user)
            self.assertEqual(role.user_id, role.user.id)

            user = mixer.blend(User)
            self.assertTrue(user.id)
            self.assertTrue(user.username)
            self.assertEqual(user.score, 50)
            self.assertTrue(user.created_at)
            self.assertTrue(user.profile)
            self.assertEqual(user.profile.user, user)

            user = mixer.blend(User, username='test')
            self.assertEqual(user.username, 'test')

            role = mixer.blend('tests.test_flask.Role', user__username='test2')
            self.assertEqual(role.user.username, 'test2')

            users = User.query.all()
            role = mixer.blend('tests.test_flask.Role', user=mixer.select)
            self.assertTrue(role.user in users)

            role = mixer.blend('tests.test_flask.Role', user=mixer.random)
            self.assertTrue(role.user)

            profile = mixer.blend('tests.test_flask.Profile')
            user = mixer.blend(User, profile=profile)
            self.assertEqual(user.profile, profile)

            user = mixer.blend(User, score=mixer.random)
            self.assertNotEqual(user.score, 50)

            user = mixer.blend(User, username=lambda: 'callable_value')
            self.assertEqual(user.username, 'callable_value')

    def test_default_mixer(self):
        from mixer.backend.flask import mixer

        test = mixer.blend(User)
        self.assertTrue(test.username)

# lint_ignore=F0401
