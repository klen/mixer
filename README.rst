|logo| Mixer
############

.. _description:

Mixer is simply application to generate instances of Django or SQLAlchemy models. It's useful for testing or fixtures replacement.
Fast and convenient test-data generation.

Mixer supports:

    - Django_;
    - SQLAlchemy_;
    - Flask-SqlAlchemy (only for python 2.6, 2.7);
    - Custom schemes;

.. _badges:

.. image:: https://secure.travis-ci.org/klen/mixer.png?branch=develop
    :target: http://travis-ci.org/klen/mixer
    :alt: Build Status

.. image:: https://coveralls.io/repos/klen/mixer/badge.png?branch=develop
    :target: https://coveralls.io/r/klen/mixer
    :alt: Coverals

.. image:: https://pypip.in/v/mixer/badge.png
    :target: https://crate.io/packages/mixer
    :alt: Version

.. image:: https://pypip.in/d/mixer/badge.png
    :target: https://crate.io/packages/mixer
    :alt: Downloads

.. image:: https://dl.dropboxusercontent.com/u/487440/reformal/donate.png
    :target: https://www.gittip.com/klen/
    :alt: Donate


.. _documentation:

Docs are available at https://mixer.readthedocs.org/. Pull requests with documentation enhancements and/or fixes are awesome and most welcome.

Описание на русском языке: http://klen.github.io/mixer-ru.html


.. _contents:

.. contents::


.. _requirements:

Requirements
=============

- python (2.6, 2.7, 3.2, 3.3)
- Django (1.4, 1.5) for django ORM suport;
- SQLAlchemy for SQLAlchemy ORM suport;
- Flask-SQLALchemy for SQLAlchemy ORM suport and integration as Flask application;


.. _installation:

Installation
=============

**Mixer** should be installed using pip: ::

    pip install mixer


.. _usage:

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


.. _bagtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/mixer/issues


.. _contributing:

Contributing
============

Development of starter happens at github: https://github.com/klen/mixer


.. _contributors:

Contributors
=============

* klen_ (horneds@gmail.com)


.. _license:

License
=======

Licensed under a `BSD license`_.


.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: http://klen.github.io
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Flask: http://flask.pocoo.org/
.. _Django: http://djangoproject.org/
.. |logo| image:: https://raw.github.com/klen/mixer/develop/docs/_static/logo.png
                  :width: 100
