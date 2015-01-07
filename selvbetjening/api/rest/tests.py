import datetime
import simplejson

from django.core.urlresolvers import reverse
from django.test import TestCase

from provider.oauth2.models import AccessToken, Client
from selvbetjening.core.events.models import Event, Attend

from selvbetjening.core.members.models import SUser


class RestAPITestCase(TestCase):

    fixtures = ['rest-api-tests.json']

    def setUp(self):
        AccessToken.objects.create(
            user=SUser.objects.get(pk=1),
            token='abc',
            client=Client.objects.get(pk=1)
        )

    def test_no_access_code(self):

        url = '/api/rest/v1/authenticated_user/?format=json'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, '')

    def test_incorrect_access_code(self):

        url = '/api/rest/v1/authenticated_user/?access_key=SOMETHINGWRONG&format=json'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, '')

    def test_only_one_authenticated_user_returned(self):

        url = '/api/rest/v1/authenticated_user/?access_key=abc&format=json'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        json = simplejson.loads(response.content)

        self.assertEqual(len(json['objects']), 1)
        self.assertEqual(json['objects'][0]['username'], 'admin')

    def test_correct_list_of_events(self):

        url = '/api/rest/v1/authenticated_user/?access_key=abc&format=json'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        json = simplejson.loads(response.content)

        self.assertEqual(len(json['objects']), 1)
        events = json['objects'][0]['events_accepted']
        self.assertEqual(len(events), 0)

        # Create three events and attend two

        event = Event.objects.create(title='test', startdate=datetime.date.today(), enddate=datetime.date.today())
        Attend.objects.create(event=event, user=SUser.objects.get(pk=1))

        event = Event.objects.create(title='test2', startdate=datetime.date.today(), enddate=datetime.date.today())
        Attend.objects.create(event=event, user=SUser.objects.get(pk=1))

        Event.objects.create(title='test3', startdate=datetime.date.today(), enddate=datetime.date.today())

        # Check if the list contains our two events

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        json = simplejson.loads(response.content)

        self.assertEqual(len(json['objects']), 1)
        events = json['objects'][0]['events_accepted']
        self.assertEqual(len(events), 2)

