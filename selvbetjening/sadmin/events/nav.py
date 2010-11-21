from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from selvbetjening.sadmin.base import nav

# events submenu
events_menu = nav.Navigation(_('Events'))
nav.registry['main'].register(events_menu)

events_menu.register(nav.Option(_(u'Browse Events'), 'sadmin:events_list',
    lambda user: user.has_perm('events.change_event'))
)

events_menu.register(nav.Option(_(u'Create Event'), 'sadmin:events_create',
    lambda user: user.has_perm('events.add_event'))
)

# event menu
event_menu = nav.Navigation()
nav.registry['event'] = event_menu

event_menu.register(nav.Option(_(u'Attendees'),
    lambda ctx: reverse('sadmin:events_view_attendees', kwargs={'event_id': ctx['event'].pk}),
    lambda user: user.has_perm('events.change_event'))
)

event_menu.register(nav.Option(_(u'Statistics'),
    lambda ctx: reverse('sadmin:events_view_statistics', kwargs={'event_id': ctx['event'].pk}),
    lambda user: user.has_perm('events.change_event'))
)

event_menu.register(nav.Option(_(u'Settings'),
    lambda ctx: reverse('sadmin:events_update', kwargs={'event_id': ctx['event'].pk}),
    lambda user: user.has_perm('events.change_event'))
)