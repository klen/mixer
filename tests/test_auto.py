from __future__ import absolute_import

try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase


class MixerTestAuto(TestCase):

    def test_main(self):
        from mixer.auto import mixer

        self.assertTrue(mixer)

    def test_django(self):
        from django.core.management import call_command
        from mixer.auto import mixer

        from .django_app.models import Rabbit

        call_command('syncdb', interactive=False)

        rabbit = mixer.blend(Rabbit)
        self.assertTrue(rabbit)

        rabbit = mixer.blend('tests.django_app.models.Rabbit')
        self.assertTrue(rabbit)

        rabbits = mixer.cycle(2).blend(Rabbit)
        self.assertTrue(all(rabbits))

        call_command('flush', interactive=False)

    def test_sqlalchemy(self):
        from mixer.auto import mixer

        from .test_sqlalchemy import User

        user = mixer.blend(User)
        self.assertTrue(user)

        user = mixer.blend('tests.test_sqlalchemy.User')
        self.assertTrue(user)

        users = mixer.cycle(2).blend(User)
        self.assertTrue(all(users))

    def test_mongoengine(self):
        from mixer.backend.mongoengine import mixer as m
        m.params['commit'] = False

        from mixer.auto import mixer

        from .test_mongoengine import User

        user = mixer.blend(User)
        self.assertTrue(user)

        user = mixer.blend('tests.test_mongoengine.User')
        self.assertTrue(user)

        users = mixer.cycle(2).blend(User)
        self.assertTrue(all(users))
