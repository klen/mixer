Mixer
#####

Mixer is simply application for generate instances of Django or SQLAlchemy models. It's useful for testing or fixtures replacement.
Fast and convenient test-data generation.

Mixer supports:

    - Django_;
    - SQLAlchemy_;
    - Flask-SqlAlchemy (only for python 2.6, 2.7);
    - Custom schemes;

.. image:: https://secure.travis-ci.org/klen/mixer.png?branch=develop
    :target: http://travis-ci.org/klen/mixer
    :alt: Build Status

.. contents::


Requirements
=============

- python (2.6, 2.7, 3.2, 3.3)
- Django (1.4, 1.5) for django ORM suport;
- SQLAlchemy for SQLAlchemy ORM suport;
- Flask-SQLALchemy for SQLAlchemy ORM suport and integration as Flask application;


Installation
=============

**Mixer** should be installed using pip: ::

    pip install mixer


Usage
=====

 |   By default Mixer try to generate fake data. If you want randomize values
 |   initialize the Mixer by manual like: Mixer(fake=False)

 |   By default Mixer saves generated objects in database. If you want disable
 |   this, initialize the Mixer by manual like: Mixer(commit=False)

Django
------
Quick example: ::

    from mixer.backend.django import mixer
    from customapp.models import User, UserMessage

    # Generate random User
    user = mixer.blend(User)

    # Generate UserMessage
    message = mixer.blend(UserMessage, user=user)

    # Generate UserMessage and User. Set User.username to 'testname'.
    message = mixer.blend(UserMessage, user__username='testname')

    # Generate SomeModel from SomeApp and select FK or M2M values from db
    some = mixer.blend('someapp.somemodel', somerelation=mixer.select)

    # Generate SomeModel from SomeApp and force a value of field with default to random
    some = mixer.blend('someapp.somemodel', money=mixer.random)

    # Generate 5 SomeModel instances and get a field values from custom generator
    some_models = mixer.cycle(5).blend('someapp.somemodel', company=(company for company in companies))


Flask, Flask-SQLAlchemy
-----------------------
Quick example: ::

    from mixer.backend.flask import mixer
    from models import User, UserMessage

    mixer.init_app(self.app)

    # Generate random User
    user = mixer.blend(User)

    # Generate UserMessage
    message = mixer.blend(UserMessage, user=user)

    # Generate UserMessage and User. Set User.username to 'testname'.
    message = mixer.blend(UserMessage, user__username='testname')

    # Generate SomeModel and select FK or M2M values from db
    some = mixer.blend('project.models.SomeModel', somerelation=mixer.select)

    # Generate SomeModel from SomeApp and force a value of field with default to random
    some = mixer.blend('project.models.SomeModel', money=mixer.random)

    # Generate 5 SomeModel instances and get a field values from custom generator
    some_models = mixer.cycle(5).blend('project.models.SomeModel', company=(company for company in companies))


SQLAlchemy
----------
Example of initialization: ::

    from mixer.backend.sqlalchemy import Mixer

    ENGINE = create_engine('sqlite:///:memory:')
    BASE = declarative_base()
    SESSION = sessionmaker(bind=ENGINE)

    mixer = Mixer(session=SESSION(), commit=True)
    role = mixer.blend('package.models.Role')


Also see `Flask, Flask-SQLALchemy`_.


Common usage
------------
Quick example: ::

        from mixer.main import Mixer

        class Test:
            one = int
            two = int
            name = str

        class Scheme:
            name = str
            money = int
            male = bool
            prop = Test

        scheme = mixer.blend(Sheme, prop__one=1)


Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/mixer/issues


Contributing
============

Development of starter happens at github: https://github.com/klen/mixer


Contributors
=============

* klen_ (horneds@gmail.com)


License
=======

Licensed under a `BSD license`_.


.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: http://klen.github.io
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Flask: http://flask.pocoo.org/
.. _Django: http://djangoproject.org/
