from __future__ import absolute_import

from sqlalchemy.orm.interfaces import MANYTOONE
from .sqlalchemy import TypeMixer as BaseTypeMixer, Mixer as BaseMixer


class TypeMixer(BaseTypeMixer):

    def gen_relation(self, target, fname, field):
        relation = field.scheme
        if relation.direction == MANYTOONE:
            col = relation.local_remote_pairs[0][0]
            if col.nullable and not field.params:
                return False

            mixer = TypeMixer(relation.mapper.class_)
            value = mixer.blend(**field.params)

            setattr(target, relation.key, value)
            setattr(target, col.name,
                    relation.mapper.identity_key_from_instance(value)[1][0])


class Mixer(BaseMixer):

    type_mixer_cls = TypeMixer

    def __init__(self, app=None, commit=False, **kwargs):
        super(Mixer, self).__init__(**kwargs)
        self.commit = commit
        if app:
            self.init_app(app)

    def init_app(self, app):
        """This callback can be used to initialize an application for the
        use with this mixer setup.

        :param app: Flask application
        """
        assert app.extensions and app.extensions[
            'sqlalchemy'], "Flask-SQLAlchemy must be inialized before Mixer."
        self.db = app.extensions['sqlalchemy'].db
        self.session = self.db.session

        # register extension with app
        app.extensions['mixer'] = self

# lint_ignore=W0201
