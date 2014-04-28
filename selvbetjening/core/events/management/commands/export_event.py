import codecs
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    args = 'event_pk'

    def handle(self, event_pk=None, target_file=None, **kwargs):

        from selvbetjening.core.events.models import Event
        from selvbetjening.core.events.models import Attend
        from selvbetjening.core.events.models import AttendState
        from selvbetjening.core.events.options.dynamic_selections import dynamic_options, dynamic_selections
        from selvbetjening.core.events.options.scope import SCOPE

        if event_pk is None:

            print 'Select an event pk:'
            for event in Event.objects.all():
                print '%s (pk=%s)' % (event, event.pk)

            return

        fp = codecs.open(target_file, 'w', 'utf-8')

        event = Event.objects.get(pk=int(event_pk))
        attendees = Attend.objects.filter(event=event).select_related().prefetch_related('selection_set')

        partial = [
            'checked_in', 'pk', 'username', 'name', 'email', 'price', 'paid'
        ]

        for option, selection in dynamic_options(SCOPE.VIEW_SYSTEM_INVOICE, event):
            partial.append(option.name)

        fp.write(u','.join(partial))
        fp.write('\n')

        for attendee in attendees:

            if attendee.state == AttendState.attended:
                attended = 'x'
            elif attendee.state == AttendState.accepted:
                attended = ''
            else:
                attended = '!!!'

            partial = [
                attended,
                str(attendee.pk),
                attendee.user.username,
                '%s %s' % (attendee.user.first_name, attendee.user.last_name),
                attendee.user.email,
                str(attendee.price),
                str(attendee.paid),

            ]

            for option, selection in dynamic_selections(SCOPE.VIEW_SYSTEM_INVOICE, attendee):
                partial.append('x' if selection is not None else '')

            fp.write(u','.join(partial))
            fp.write('\n')

        fp.close()
