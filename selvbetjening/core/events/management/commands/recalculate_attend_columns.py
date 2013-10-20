
from django.core.management.base import NoArgsCommand

from selvbetjening.core.events.models import Attend


class Command(NoArgsCommand):
    def handle_noargs(self, **options):

        attendees = Attend.objects.select_related().prefetch_related('selection_set')

        for attendee in attendees:
            attendee.recalculate_price()

        Attend.objects.recalculate_aggregations_paid(attendees)
