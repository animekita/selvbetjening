from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from selvbetjening.sadmin.base import nav

## main menu
#nav.registry['main'].register(
    #nav.Option(_(u'Events'),
               #'sadmin:events_event_changelist',
               #lambda user: user.has_perm('events.change_event'))
#)

## events menu

#events_menu = nav.Navigation()

#events_menu.register(nav.Option(_(u'Browse Events'),
    #'sadmin:events_event_changelist',
    #lambda user: user.has_perm('events.change_event'))
#)

#events_menu.register(nav.Option(_(u'Create Event'),
    #'sadmin:events_event_add',
    #lambda user: user.has_perm('events.add_event')),
#)

#events_menu.register(nav.Option(_(u'Register Payment'),
    #'sadmin:events_event_register_payment',
    #lambda user: user.has_perm('events.add_event'))
#)

## event menu
#event_menu = nav.Navigation()

#event_menu.register(nav.Option(_(u'Event'),
    #lambda ctx: reverse('sadmin:events_event_change',
                        #args=[ctx['event_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#event_menu.register(nav.Option(_(u'Statistics'),
    #lambda ctx: reverse('sadmin:events_event_statistic',
                        #kwargs={'event_pk': ctx['event_pk']}),
    #lambda user: user.has_perm('events.change_event'))
#)

#event_menu.register(nav.Option(_(u'Financial Report'),
    #lambda ctx: reverse('sadmin:events_event_financial',
                        #kwargs={'event_pk': ctx['event_pk']}),
    #lambda user: user.has_perm('events.change_event'))
#)

#event_menu.register(nav.Option(_(u'Attendees'),
    #lambda ctx: reverse('sadmin:events_attendee_changelist',
                        #args=[ctx['event_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#event_menu.register(nav.Option(_(u'Add attendee'),
    #lambda ctx: reverse('sadmin:events_nonattendee_changelist',
                        #args=[ctx['event_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#event_menu.register(nav.Option(_(u'Option groups'),
    #lambda ctx: reverse('sadmin:events_optiongroup_changelist',
                        #args=[ctx['event_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#event_menu.register(nav.Option(_(u'Add option group'),
    #lambda ctx: reverse('sadmin:events_optiongroup_add',
                        #args=[ctx['event_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

## attendee menu
#attendee_menu = nav.Navigation()

#attendee_menu.register(nav.Option(_(u'< To Event'),
    #lambda ctx: reverse('sadmin:events_attendee_changelist',
                        #args=[ctx['event_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#attendee_menu.register(nav.Option(_(u'Attendee'),
    #lambda ctx: reverse('sadmin:events_attendee_change',
                        #args=[ctx['event_pk'], ctx['attendee_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#attendee_menu.register(nav.Option(_(u'Selections'),
    #lambda ctx: reverse('sadmin:events_attendee_selections',
                        #args=[ctx['event_pk'], ctx['attendee_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#attendee_menu.register(nav.Option(_(u'Invoice'),
    #lambda ctx: reverse('sadmin:events_invoice_change',
                        #args=[ctx['event_pk'], ctx['attendee_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#attendee_menu.register(nav.Option(_(u'PKs'),
    #lambda ctx: reverse('sadmin:events_attendee_show_pks',
                        #args=[ctx['event_pk'], ctx['attendee_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#attendee_menu.register(nav.Option(_(u'User Profile'),
    #lambda ctx: reverse('sadmin:members_user_change',
                        #args=[ctx['user_pk']]),
    #lambda user: user.has_perm('auth.change_user'))
#)

## option group menu
#optiongroup_menu = nav.Navigation()

#optiongroup_menu.register(nav.Option(_(u'< To Event'),
    #lambda ctx: reverse('sadmin:events_optiongroup_changelist',
                        #args=[ctx['event_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#optiongroup_menu.register(nav.Option(_(u'Settings'),
    #lambda ctx: reverse('sadmin:events_optiongroup_change',
                        #args=[ctx['event_pk'], ctx['optiongroup_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#optiongroup_menu.register(nav.Option(_(u'Options'),
    #lambda ctx: reverse('sadmin:events_option_changelist',
                        #args=[ctx['event_pk'], ctx['optiongroup_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)

#optiongroup_menu.register(nav.Option(_(u'Add option'),
    #lambda ctx: reverse('sadmin:events_option_add',
                        #args=[ctx['event_pk'], ctx['optiongroup_pk']]),
    #lambda user: user.has_perm('events.change_event'))
#)