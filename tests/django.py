from __future__ import absolute_import

from unittest import TestCase


class MixerTestDjango(TestCase):

    def test_base(self):
        from mixer.backend.django import Mixer

        mixer = Mixer()
        rabbit = mixer.blend('django_app.rabbit')
        self.assertEqual(len(rabbit.title), 16)
