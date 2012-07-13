"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

from selvbetjening.core.events.tests import Database as EventDatabase

from utility import translate_model
from models import Translation

class TranslationUtilityTest(TestCase):
    def test_translate_model(self):
        event = EventDatabase.new_event()

        Translation.objects.create(translated_object=event, field='title', locale='na-na', translation=u'na text')

        title = event.title

        translate_model(event, 'na-na')

        self.assertNotEqual(event.title, title)


