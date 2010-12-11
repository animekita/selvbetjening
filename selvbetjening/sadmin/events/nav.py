from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from selvbetjening.sadmin.base import nav

# events submenu
events_menu = nav.Navigation(_('Events'))
nav.registry['main'].register(events_menu)

events_menu.register(nav.Option(_(u'Browse Events'), 'sadmin:events_event_changelist',
    lambda user: user.has_perm('events.change_event'))
)

events_menu.register(nav.Option(_(u'Create Event'), 'sadmin:events_event_add',
    lambda user: user.has_perm('events.add_event'))
)

# event menu
event_menu = nav.Navigation()
nav.registry['event'] = event_menu

event_menu.register(nav.Option(_(u'Attendees'),
    lambda ctx: reverse('sadmin:events_attendee_changelist', args=[ctx['original'].pk]),
    lambda user: user.has_perm('events.change_event'))
)

event_menu.register(nav.Option(_(u'Statistics'),
    lambda ctx: reverse('sadmin:events_event_statistic', kwargs={'event_pk': ctx['original'].pk}),
    lambda user: user.has_perm('events.change_event'))
)

event_menu.register(nav.Option(_(u'Settings'),
    lambda ctx: reverse('sadmin:events_event_change', args=[ctx['original'].pk]),
    lambda user: user.has_perm('events.change_event'))
)

# attendee menu
attendee_menu = nav.Navigation()
nav.registry['attendee_menu'] = attendee_menu

attendee_menu.register(nav.Option(_(u'< To Event'),
    lambda ctx: reverse('sadmin:events_attendee_changelist', args=[ctx['event'].pk]),
    lambda user: user.has_perm('events.change_event'))
)

attendee_menu.register(nav.Option(_(u'Registration'),
    lambda ctx: reverse('sadmin:events_attendee_change', args=[ctx['event'].pk, ctx['attendee']]),
    lambda user: user.has_perm('events.change_event'))
)

