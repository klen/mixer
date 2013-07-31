.. _quickstart:

Quickstart
==========

.. contents::

.. currentmodule:: mixer.main

Mixer is easy to use and realy fun for testing applications.
Module has a common api for all backends (Django_, Flask_).

Django ORM
----------

Models
^^^^^^

Somewhere in 'someapp/models.py':

.. code-block:: python

        from django.db import models

        class Client(models.Model):
            username = models.CharField(max_length=20)
            name = models.CharField(max_length=50)
            created_at = models.DateField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)
            score = models.IntegerField(default=50)

        class Message(models.Model):
            content = models.TextField()
            client = models.ForeignKey(Client)

        class Tag(models.Model):
            title = models.CharField(max_length=20)
            messages = models.ManyToManyField(Message, null=True, blank=True)


Base Usage
^^^^^^^^^^

You can use class or string with model name.

.. [1] Model name supports two formats. Use 'app_name.model_name' for prevent conflicts.
       Or you can use just 'model_name' for models with unique names.

.. [2] `model_name` is case insensitive.

.. code-block:: python

    from mixer.backend.django import mixer

    # Generate model's instance and save to db
    message = mixer.blend('someapp.message')

    print message.content  # Some like --> necessitatibus voluptates animi molestiae dolores...

    print message.client.username  # Some like --> daddy102

    print message.client.name  # Some like --> Clark Llandrindod

    # Generate a few pieces
    messages = mixer.cycle(4).blend('someapp.message')


Blend models with values
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from mixer.backend.django import mixer

    # Generate model with some values
    client = mixer.blend(Client, username='test')
    assert client.username == 'test'

    # Generate model with reference
    message = mixer.blend(Message, client__username='test2')
    assert message.client.username == 'test2'

    # Value may be callable
    client = mixer.blend(Client, username=lambda:'callable_value')
    assert client.username == 'callable_value'

    # Value may be a generator
    clients = mixer.cycle(4).blend(Client, username=(name for name in ('Piter', 'John')))

    # Value could be getting a counter
    clients = mixer.cycle(4).blend(Client, username=mixer.sequence(lambda c: "test_%s" % c))
    print clients[2].username  # --> 'test_2'

    # Short format for string formating
    clients = mixer.cycle(4).blend(Client, username=mixer.sequence("test_{0}"))
    print clients[2].username  # --> 'test_2'

    # Force to generation of a default (or null) values
    client = mixer.blend(Client, score=mixer.random)
    print client.score  # Some like: --> 456

    # Set related values from db by random
    message = mixer.blend(Message, client=mixer.select)
    assert message.client in Client.objects.all()


SQLAlchemy ORM
--------------

.. code-block:: python

    from mixer.backend.sqlalchemy import mixer

    # Generate model's instance and save to db
    message = mixer.blend('path.to.module.ModelClass')

    print message.content  # Some like --> necessitatibus voluptates animi molestiae dolores...

    print message.client.username  # Some like --> daddy102

    print message.client.name  # Some like --> Clark Llandrindod

    # Generate a few pieces
    messages = mixer.cycle(4).blend('path.to.module.ModelClass')


Flask integration
-----------------

.. automodule:: mixer.backend.flask


Mongoengine
-----------

.. automodule:: mixer.backend.mongoengine


.. == links ==
.. _links:
.. include:: ../README.rst
    :start-after: .. _links:
