from __future__ import absolute_import

import datetime

from django.test import TestCase
from django.core.management import call_command


class MixerTestDjango(TestCase):

    @classmethod
    def setUpClass(cls):
        call_command('syncdb')

    @classmethod
    def tearDownClass(cls):
        call_command('flush', interactive=False)

    def test_base(self):
        from mixer.backend.django import Mixer

        mixer = Mixer(commit=True)
        rabbit = mixer.blend('django_app.rabbit')

        self.assertTrue(rabbit.id)
        self.assertTrue(rabbit.pk)
        self.assertEqual(rabbit.pk, 1)
        self.assertEqual(len(rabbit.title), 16)
        self.assertTrue(isinstance(rabbit.active, bool))
        self.assertTrue(isinstance(rabbit.created_at, datetime.date))
        self.assertTrue(isinstance(rabbit.updated_at, datetime.datetime))
        self.assertTrue(isinstance(rabbit.opened_at, datetime.time))
        self.assertTrue('@' in rabbit.email)
