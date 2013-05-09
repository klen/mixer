from unittest import TestCase


class MixerTestSQLAlchemy(TestCase):

    def setUp(self):
        from sqlalchemy import create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Column, Integer, String

        self.engine = create_engine('sqlite:///:memory:')
        self.base = declarative_base()

        class User(self.base):
            id = Column(Integer, primary_key=True)

    def test_backend(self):
        from mixer.backends.sqlalchemy import TypeMixer
