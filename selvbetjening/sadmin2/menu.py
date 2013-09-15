# coding=utf-8

"""

    Breadcrumbs

    A breadcrumb consist of a sequence of items, each rendered as a link to a page in sadmin2.

    For each unique sequence you will need to add an entry to the breadcrumbs dictionary. The
    sequence will be calculated by following the entry's parent pointer recursively.

    Rendering and recursive traversal of the breadcrumbs are handled by the sadmin2_breadcrumbs
    template tag.

    Each entry consists of an ID (the key) referenced by the parent properties, and a
    dictionary with the following keys.

    name (required if no name_callback): A label for the item.
    name_callback (required if no name): A function returning a label for the item. The current context is given as the first argument.
    url (optional): A string resolvable to a URL if used in the {% url %} template tag
    url_callback (optional): A function returning a full url. The current context is given as the first argument.
    parent (optional): A string pointing to an existing parent entry.
                       The traversal stops if this value is None or omitted.


"""

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _


def url_callback(url):
    """
    A quick shortcut for passing kwargs in the current request context to URLs we want to generate.

    This assumes the naming of kwargs to be consistent across pages.

    """
    return lambda context: reverse_lazy(url, kwargs=context['request'].resolver_match.kwargs)


breadcrumbs = {
    'dashboard': {'name': _('Dashboard'),
                  'url': 'sadmin2:dashboard'},

    'events': {'name': _('Events'),
               'url': 'sadmin2:events_list',
               'parent': 'dashboard'},

    'events_create': {'name': _('Create'),
                      'url': 'sadmin2:events_create',
                      'parent': 'events'},

    'events_register_payments': {'name': _('Register Payments'),
                                 'url': 'sadmin2:events_register_payments',
                                 'parent': 'events'},

    # Assumes: context[event], kwargs[event_pk]
    'event': {'name_callback': lambda context: context['event'].title,
              'url_callback': url_callback('sadmin2:event_attendees'),
              'parent': 'events'},

    # Assumes: context[event], kwargs[event_pk]
    'event_account':  {
        'name': _('Account'),
        'url_callback': url_callback('sadmin2:event_account'),
        'parent': 'event'},

    # Assumes: context[event], kwargs[event_pk]
    'event_settings':  {
        'name': _('Settings'),
        'url_callback': url_callback('sadmin2:event_settings'),
        'parent': 'event'},

    # Assumes: context[event], kwargs[event_pk]
    'event_statistics':  {
        'name': _('Statistics'),
        'url_callback': url_callback('sadmin2:event_statistics'),
        'parent': 'event'},
}

sadmin2_menu_main = (
    {'id': 'events', 'name': _('Events'), 'url': 'sadmin2:events_list'},
    {'id': 'users', 'name': _('Users'), 'url': 'sadmin:auth_user_changelist'},
    {'id': 'emails', 'name': _('Newsletters'), 'url': 'sadmin:mailcenter_emailspecification_changelist'}
)

sadmin2_menu_tab_events = (
    {'id': 'events', 'name': _('Events'), 'url': 'sadmin2:events_list'},
    {'id': 'events_register_payments', 'name': _('Register Payment'), 'url': 'sadmin2:events_register_payments'},
    {'id': 'events_create', 'name': _('Create '), 'url': 'sadmin2:events_create', 'icon': 'plus', 'class': 'pull-right'}
)

# Assumes kwargs[event_pk]
sadmin2_menu_tab_event = (
    {'id': 'attendees',
     'name': u'Deltagere',
     'url_callback': url_callback('sadmin2:event_attendees')},

    {'id': 'statistics',
     'name': u'Statistik',
     'url_callback': url_callback('sadmin2:event_statistics')},

    {'id': 'account',
     'name': _('Account'),
     'url_callback': url_callback('sadmin2:event_account')},

    {'id': 'settings',
     'name': u'Settings',
     'dropdown': (
         {'id': 'settings-event',
          'name': u'Arrangement',
          'url_callback': url_callback('sadmin2:event_settings'),
          },

         {'id': 'settings-selections',
          'name': u'Tilvalg',
          'url_callback': url_callback('sadmin2:event_settings_selections')
          }
     )},

    {'id': 'add',
     'name': _('Add attendee'),
     'dropdown': (
         {'id': 'add-existing',
          'name': _('Existing user'),
          'url_callback': url_callback('sadmin2:event_settings'),
          },

         {'id': 'add-new',
          'name': _('New user'),
          'url_callback': url_callback('sadmin2:event_settings_selections')
          }),
     'class': 'pull-right'
     },
)


sadmin2_menu_manifest = {
    'sadmin2_menu_main': sadmin2_menu_main
}
