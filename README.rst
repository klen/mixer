|logo| Mixer
############

Mixer is an application to generate instances of Django or SQLAlchemy models.
It's useful for testing and fixtures replacement. Fast and convenient test-data
generation.

Mixer supports:

* Django_;
* SQLAlchemy_;
* Flask-SQLAlchemy_;
* Peewee_;
* Pony_;
* Mongoengine_;
* Marshmallow_;
* Custom schemes;

.. _badges:

.. image:: http://img.shields.io/travis/klen/mixer.svg?style=flat-square
    :target: http://travis-ci.org/klen/mixer
    :alt: Build Status

.. image:: http://img.shields.io/coveralls/klen/mixer.svg?style=flat-square
    :target: https://coveralls.io/r/klen/mixer
    :alt: Coverals

.. image:: http://img.shields.io/pypi/v/mixer.svg?style=flat-square
    :target: https://pypi.python.org/pypi/mixer
    :alt: Version

.. image:: http://img.shields.io/pypi/dm/mixer.svg?style=flat-square
    :target: https://pypi.python.org/pypi/mixer
    :alt: Downloads

.. image:: http://img.shields.io/pypi/l/mixer.svg?style=flat-square
    :target: https://pypi.python.org/pypi/mixer
    :alt: License


.. _documentation:


**Docs are available at https://mixer.readthedocs.org/. Pull requests with
documentation enhancements and/or fixes are awesome and most welcome.**

Описание на русском языке: http://klen.github.io/mixer.html


.. _contents:

.. contents::


Requirements
=============

- python (2.6, 2.7, 3.2, 3.3, 3.4)
- fake-factory >= 0.5.0
- Django (1.10, 1.11, 2.0) for Django ORM support;
- SQLAlchemy for SQLAlchemy ORM support;
- Mongoengine for Mongoengine ODM support;
- Flask-SQLALchemy for SQLAlchemy ORM support and integration as Flask application;


Installation
=============

**Mixer** should be installed using pip: ::

    pip install mixer


Usage
=====

 |   By default Mixer tries to generate a fake (human-friendly) data.
 |   If you want to randomize the generated values initialize the Mixer
 |   by manual: Mixer(fake=False)


 |   By default Mixer saves the generated objects in a database. If you want to disable
 |   this, initialize the Mixer by manual like: Mixer(commit=False)


Django workflow
---------------
Quick example: ::

    from mixer.backend.django import mixer
    from customapp.models import User, UserMessage

    # Generate a random user
    user = mixer.blend(User)

    # Generate an UserMessage
    message = mixer.blend(UserMessage, user=user)

    # Generate an UserMessage and an User. Set username for generated user to 'testname'.
    message = mixer.blend(UserMessage, user__username='testname')

    # Generate SomeModel from SomeApp and select FK or M2M values from db
    some = mixer.blend('someapp.somemodel', somerelation=mixer.SELECT)

    # Generate SomeModel from SomeApp and force a value of money field from default to random
    some = mixer.blend('someapp.somemodel', money=mixer.RANDOM)

    # Generate 5 SomeModel's instances and take company field's values from custom generator
    some_models = mixer.cycle(5).blend('somemodel', company=(name for name in company_names))


Flask, Flask-SQLAlchemy
-----------------------
Quick example: ::

    from mixer.backend.flask import mixer
    from models import User, UserMessage

    mixer.init_app(self.app)

    # Generate a random user
    user = mixer.blend(User)

    # Generate an userMessage
    message = mixer.blend(UserMessage, user=user)

    # Generate an UserMessage and an User. Set username for generated user to 'testname'.
    message = mixer.blend(UserMessage, user__username='testname')

    # Generate SomeModel and select FK or M2M values from db
    some = mixer.blend('project.models.SomeModel', somerelation=mixer.SELECT)

    # Generate SomeModel from SomeApp and force a value of money field from default to random
    some = mixer.blend('project.models.SomeModel', money=mixer.RANDOM)

    # Generate 5 SomeModel's instances and take company field's values from custom generator
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


SQLAlchemy workflow
-------------------

Example of initialization: ::

    from mixer.backend.sqlalchemy import Mixer

    ENGINE = create_engine('sqlite:///:memory:')
    BASE = declarative_base()
    SESSION = sessionmaker(bind=ENGINE)

    mixer = Mixer(session=SESSION(), commit=True)
    role = mixer.blend('package.models.Role')


Also, see `Flask, Flask-SQLALchemy`_.


Mongoengine workflow
--------------------

Example usage: ::

    from mixer.backend.mongoengine import mixer

    class User(Document):
        created_at = DateTimeField(default=datetime.datetime.now)
        email = EmailField(required=True)
        first_name = StringField(max_length=50)
        last_name = StringField(max_length=50)
        username = StringField(max_length=50)

    class Post(Document):
        title = StringField(max_length=120, required=True)
        author = ReferenceField(User)
        tags = ListField(StringField(max_length=30))

    post = mixer.blend(Post, author__username='foo')

Marshmallow workflow
--------------------

Example usage: ::

    from mixer.main import mixer
    import marshmallow as ma

    class User(ma.Schema):
        created_at = ma.fields.DateTime(required=True)
        email = ma.fields.Email(required=True)
        first_name = ma.fields.String(required=True)
        last_name = ma.fields.String(required=True)
        username = ma.fields.String(required=True)

    class Post(ma.Schema):
        title = ma.fields.String(required=True)
        author = ma.fields.Nested(User, required=True)

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

By default 'django', 'flask', 'mongoengine' backends tries to save objects in
database. For preventing this behavior init `mixer` manually: ::

    from mixer.backend.django import Mixer

    mixer = Mixer(commit=False)


Or you can temporary switch context use the mixer as context manager: ::

    from mixer.backend.django import mixer

    # Will be save to db
    user1 = mixer.blend('auth.user')

    # Will not be save to db
    with mixer.ctx(commit=False):
        user2 = mixer.blend('auth.user')


.. _custom:

Custom fields
-------------

Mixer allows you to define generators for fields by manually.

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

Also, you can make your own factory for field types: ::

    from mixer.backend.django import Mixer, GenFactory

    def get_func(*args, **kwargs):
        return "Always same"

    class MyFactory(GenFactory):
        generators = {
            models.CharField: get_func
        }

    mixer = Mixer(factory=MyFactory)

Middlewares
-----------

You can add middleware layers to process generation: ::

    from mixer.backend.django import mixer

    # Register middleware to model
    @mixer.middleware('auth.user')
    def encrypt_password(user):
        user.set_password('test')
        return user

You can add several middlewares. Each middleware should get one argument
(generated value) and return them.

Locales
-------

By default mixer uses 'en' locale. You could switch mixer default locale by
creating your own mixer: ::

    from mixer.backend.django import Mixer

    mixer = Mixer(locale='it')
    mixer.faker.name()          ## u'Acchisio Conte'

At any time you could switch mixer current locale: ::

    mixer.faker.locale = 'cz'
    mixer.faker.name()          ## u'Miloslava Urbanov\xe1 CSc.'

    mixer.faker.locale = 'en'
    mixer.faker.name()          ## u'John Black'

    # Use the mixer context manager
    mixer.faker.phone()         ## u'1-438-238-1116'
    with mixer.ctx(locale='fr'):
        mixer.faker.phone()     ## u'08 64 92 11 79'

    mixer.faker.phone()         ## u'1-438-238-1116'

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/mixer/issues


Contributing
============

Development of mixer happens at Github: https://github.com/klen/mixer


Contributors
=============

* Antoine Bertin      (https://github.com/Diaoul)
* Benjamin Port       (https://github.com/bport)
* Dmitriy Moseev      (https://github.com/DmitriyMoseev)
* Eelke Hermens       (https://github.com/eelkeh)
* Esteban J. G. Gabancho (https://github.com/egabancho)
* Felix Dreissig      (https://github.com/F30)
* Illia Volochii      (https://github.com/illia-v)
* Kirill Klenov       (https://github.com/klen, horneds@gmail.com)
* Kirill Pavlov       (https://github.com/pavlov99)
* Kwok-kuen Cheung    (https://github.com/cheungpat)
* Mahdi Yusuf         (https://github.com/myusuf3)
* Marek Baczyński     (https://github.com/imbaczek)
* Matt Caldwell       (https://github.com/mattcaldwell)
* Skylar Saveland     (https://github.com/skyl)
* Suriya Subramanian  (https://github.com/suriya)


License
=======

Licensed under a `BSD license`_.


.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _Django: http://djangoproject.com/
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _Flask: http://flask.pocoo.org/
.. _Marshmallow: http://marshmallow.readthedocs.io/en/latest/
.. _Mongoengine: http://mongoengine.org/
.. _Peewee: http://peewee.readthedocs.org/en/latest/
.. _Pony: http://ponyorm.com/
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _klen: http://klen.github.io
.. |logo| image:: https://raw.github.com/klen/mixer/develop/docs/_static/logo.png
                  :width: 100
