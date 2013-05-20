from __future__ import absolute_import

import datetime
from .django_app.models import *

from django.core.management import call_command
from django.test import TestCase

from mixer.backend.django import Mixer


class MixerTestDjango(TestCase):

    @classmethod
    def setUpClass(cls):
        call_command('syncdb')

    @classmethod
    def tearDownClass(cls):
        call_command('flush', interactive=False)

    def test_fields(self):
        from .django_app.models import Rabbit

        mixer = Mixer()
        rabbit = mixer.blend('django_app.rabbit')

        self.assertTrue(isinstance(rabbit, Rabbit))
        self.assertTrue(rabbit.id)
        self.assertTrue(rabbit.pk)
        self.assertEqual(rabbit.pk, 1)
        self.assertEqual(len(rabbit.title), 16)
        self.assertTrue(isinstance(rabbit.active, bool))
        self.assertTrue(isinstance(rabbit.created_at, datetime.date))
        self.assertTrue(isinstance(rabbit.updated_at, datetime.datetime))
        self.assertTrue(isinstance(rabbit.opened_at, datetime.time))
        self.assertTrue('@' in rabbit.email)
        self.assertTrue(rabbit.speed)
        self.assertTrue(rabbit.description)

    def test_random_fields(self):
        from .django_app.models import Rabbit

        mixer = Mixer(fake=False)
        rabbit = mixer.blend('django_app.rabbit')

        self.assertTrue(isinstance(rabbit, Rabbit))
        self.assertTrue(rabbit.id)
        self.assertTrue(rabbit.pk)
        self.assertEqual(rabbit.pk, 1)
        self.assertEqual(len(rabbit.title), 16)
        self.assertTrue(isinstance(rabbit.active, bool))
        self.assertTrue(isinstance(rabbit.created_at, datetime.date))
        self.assertTrue(isinstance(rabbit.updated_at, datetime.datetime))
        self.assertTrue(isinstance(rabbit.opened_at, datetime.time))
        self.assertTrue('@' in rabbit.email)
        self.assertTrue(rabbit.description)
        self.assertTrue(rabbit.some_field)
        self.assertTrue(rabbit.money)

    def test_relation(self):
        mixer = Mixer()

        hole = mixer.blend('django_app.hole', title='hole4')
        self.assertEqual(hole.owner.pk, 1)
        self.assertEqual(hole.title, 'hole4')

        hat = mixer.blend('django_app.hat')
        self.assertFalse(hat.owner)
        self.assertEqual(hat.brend, 'wood')
        self.assertTrue(hat.color in ('RD', 'GRN', 'BL'))

        hat = mixer.blend('django_app.hat', owner=mixer.select)
        self.assertTrue(hat.owner)

        silk = mixer.blend('django_app.silk')
        self.assertFalse(silk.hat.owner)

        silk = mixer.blend('django_app.silk', hat__owner__title='booble')
        self.assertTrue(silk.hat.owner)
        self.assertEqual(silk.hat.owner.title, 'booble')

        door = mixer.blend('django_app.door', hole__title='flash',
                           hole__size=244)
        self.assertTrue(door.hole.owner)
        self.assertEqual(door.hole.title, 'flash')
        self.assertEqual(door.hole.size, 244)

        door = mixer.blend('django_app.door')
        self.assertNotEqual(door.hole.title, 'flash')

        num = mixer.blend('django_app.number', doors=[door])
        self.assertEqual(num.doors.get(), door)

        num = mixer.blend('django_app.number')
        self.assertEqual(num.doors.count(), 1)

        num = mixer.blend('django_app.number', doors__size=42)
        self.assertEqual(num.doors.all()[0].size, 42)

        num = mixer.blend('django_app.colornumber')
        self.assertEqual(num.doors.count(), 1)

    def test_default_mixer(self):
        from mixer.backend.django import mixer

        test = mixer.blend(Rabbit)
        self.assertTrue(test.username)

    def test_select(self):
        from mixer.backend.django import mixer

        mixer.cycle(3).blend(Rabbit)
        hole = mixer.blend(Hole, rabbit=mixer.select)
        self.assertFalse(hole.rabbit)

        hole = mixer.blend(Hole, owner=mixer.select)
        self.assertTrue(hole.owner in Rabbit.objects.all())


# lint_ignore=F0401,W0401,E0602
