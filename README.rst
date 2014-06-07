|logo| Mixer
############

.. _description:

Mixer is application to generate instances of Django or SQLAlchemy models.
It's useful for testing and fixtures replacement.
Fast and convenient test-data generation.

Mixer supports:

    - Django_;
    - SQLAlchemy_;
    - Flask-SqlAlchemy;
    - Peewee_;
    - Pony_;
    - Mongoengine_;
    - Custom schemes;

.. _badges:

.. image:: https://secure.travis-ci.org/klen/mixer.png?branch=develop
    :target: http://travis-ci.org/klen/mixer
    :alt: Build Status

.. image:: https://coveralls.io/repos/klen/mixer/badge.png?branch=develop
    :target: https://coveralls.io/r/klen/mixer
    :alt: Coverals

.. .. image:: https://pypip.in/v/mixer/badge.png
    .. :target: https://crate.io/packages/mixer
    .. :alt: Version

.. .. image:: https://pypip.in/d/mixer/badge.png
    .. :target: https://crate.io/packages/mixer
    .. :alt: Downloads

.. image:: https://dl.dropboxusercontent.com/u/487440/reformal/donate.png
    :target: https://www.gittip.com/klen/
    :alt: Donate


.. _documentation:


**Docs are available at https://mixer.readthedocs.org/. Pull requests with documentation enhancements and/or fixes are awesome and most welcome.**

Описание на русском языке: http://klen.github.io/mixer-ru.html


.. _contents:

.. contents::


.. _requirements:

Requirements
=============

- python (2.6, 2.7, 3.2, 3.3)
- Django (1.4, 1.5, 1.6) for django ORM suport;
- SQLAlchemy for SQLAlchemy ORM suport;
- Mongoengine for Mongoengine ODM support;
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
    some = mixer.blend('someapp.somemodel', somerelation=mixer.SELECT)

    # Generate SomeModel from SomeApp and force a value of field with default to random
    some = mixer.blend('someapp.somemodel', money=mixer.RANDOM)

    # Generate 5 SomeModel instances and get a field values from custom generator
    some_models = mixer.cycle(5).blend('somemodel', company=(company for company in companies))


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
    some = mixer.blend('project.models.SomeModel', somerelation=mixer.SELECT)

    # Generate SomeModel from SomeApp and force a value of field with default to random
    some = mixer.blend('project.models.SomeModel', money=mixer.RANDOM)

    # Generate 5 SomeModel instances and get a field values from custom generator
    some_models = mixer.cycle(5).blend('project.models.SomeModel', company=(company for company in companies))


Support for Flask-SQLAlchemy models that have `__init__` arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For support this scheme, just create your own mixer class, like this: ::

    from mixer.backend.sqlalchemy import Mixer

    class MyOwnMixer(Mixer):

        def populate_target(self, values):
            target = self.__scheme(**values)
            return target

    mixer = MyOwnMixer()


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


Mongoengine
-----------

Example usage: ::

    from mixer.backend.mongoengine import mixer
    
    class User(Document):
        created_at = DateTimeField(default=datetime.datetime.now)
        email = EmailField(required=True)
        first_name = StringField(max_length=50)
        last_name = StringField(max_length=50)

    class Post(Document):
        title = StringField(max_length=120, required=True)
        author = ReferenceField(User)
        tags = ListField(StringField(max_length=30))

    post = mixer.blend(Post, author__username='foo')


Common usage
------------
Quick example: ::

        from mixer.main import mixer

        class Test:
            one = int
            two = int
            name = str

        class Scheme:
            name = str
            money = int
            male = bool
            prop = Test

        scheme = mixer.blend(Scheme, prop__one=1)


DB commits
----------

By default 'django', 'flask', 'mongoengine' backends tries to save objects
to database. For prevent this behaviour init `mixer` manually: ::

    from mixer.backend.django import Mixer

    mixer = Mixer(commit=False)


Or you can use mixer with custom params as context: ::

    from mixer.backend.django import mixer

    # Will be save to db
    user1 = mixer.blend('auth.user')

    # Will not be save to db
    with mixer.ctx(commit=False):
        user2 = mixer.blend('auth.user')
        

.. _custom:

Custom fields
-------------

Mixer allows you to define generators for fields by manualy.

Quick example: ::

        from mixer.main import mixer

        class Test:
            id = int
            name = str

        mixer.register(Test,
            name=lambda: 'John',
            id=lambda: str(mixer.g.get_positive_integer())
        )

        test = mixer.blend(Test)
        test.name == 'John'
        isinstance(test.id, str)

        # You could pinned just a value to field
        mixer.register(Test, name='Just John')
        test = mixer.blend(Test)
        test.name == 'Just John'

Also you can make your own factory for field types: ::

    from mixer.backend.django import Mixer, GenFactory

    def get_func(*args, **kwargs):
        return "Always same"

    class MyFactory(GenFactory):
        generators = {
            models.CharField: get_func
        }

    mixer = Mixer(factory=MyFactory)

.. _middlewares:

Middlewares
-----------

You can add middleware layers to process generation: ::

    from mixer.backend.django import mixer

    # Register middleware to model
    @mixer.middleware('auth.user')
    def encrypt_password(user):
        user.set_password('test')
        return user

You can add several middlewares.
Each middleware should get one argument (generated value) and return them.


.. _bugtracker:

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

* Kirill Klenov (horneds@gmail.com)

* Antoine Bertin (https://github.com/Diaoul)
* Mahdi Yusuf (https://github.com/myusuf3)
* Marek Baczyński (https://github.com/imbaczek)
* Matt Caldwell (https://github.com/mattcaldwell)
* Skylar Saveland (https://github.com/skyl)


.. _license:

License
=======

Licensed under a `BSD license`_.


.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: http://klen.github.io
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Flask: http://flask.pocoo.org/
.. _Peewee: http://peewee.readthedocs.org/en/latest/
.. _Pony: http://ponyorm.com/
.. _Django: http://djangoproject.org/
.. _Mongoengine: http://mongoengine.org/
.. |logo| image:: https://raw.github.com/klen/mixer/develop/docs/_static/logo.png
                  :width: 100
