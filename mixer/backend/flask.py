from __future__ import absolute_import

from .sqlalchemy import TypeMixer, Mixer as BaseMixer


class Mixer(BaseMixer):

    type_mixer_cls = TypeMixer

    def __init__(self, app=None, commit=True, **kwargs):
        """
        Initialize the SQLAlchemy Mixer.

        :param fake: (True) Generate fake data instead of random data.
        :param app: Flask application
        :param commit: (False) Commit instance to session after creation.
        """
        super(Mixer, self).__init__(**kwargs)
        self.commit = commit
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        This callback can be used to initialize an application for the
        use with this mixer setup.

        :param app: Flask application
        """
        assert app.extensions and app.extensions[
            'sqlalchemy'], "Flask-SQLAlchemy must be inialized before Mixer."
        self.db = app.extensions['sqlalchemy'].db
        self.session = self.db.session

        # register extension with app
        app.extensions['mixer'] = self


# Default mixer
mixer = Mixer()

# lint_ignore=W0201
