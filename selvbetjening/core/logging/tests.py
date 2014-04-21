from django.test import TestCase
from selvbetjening.core.events.models import Attend, Event
from selvbetjening.core.logging.models import Log
from selvbetjening.core.user.models import SUser


class LogTestCase(TestCase):
    fixtures = ['sdemo-example-site.json']

    def test_create_delete_attendee(self):
        # Test if creating an attendee creates a related log entry,
        # and that the log entry is retained when the attendee is deleted

        user = SUser.objects.get(pk=1)
        event = Event.objects.get(pk=1)
        attend = Attend.objects.create(user=user, event=event)

        self.assertEqual(Log.objects.all().count(), 1)
        self.assertEqual(Log.objects.all()[0].related_attendee, attend)

        attend.delete()

        self.assertEqual(Log.objects.all().count(), 1)
        self.assertEqual(Log.objects.all()[0].related_attendee, None)
