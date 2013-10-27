
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        from selvbetjening.core.events.models import Attend

        attendees = Attend.objects.select_related().prefetch_related('selection_set')

        for attendee in attendees:
            attendee.recalculate_price()

        Attend.objects.recalculate_aggregations_paid(attendees)
