
from django.core.management.base import NoArgsCommand

from selvbetjening.core.events.models import Attend


class Command(NoArgsCommand):
    def handle_noargs(self, **options):

        attendees = Attend.objects.all()

        Attend.objects.recalculate_aggregations_paid(attendees)
        Attend.objects.recalculate_aggregations_price(attendees)
