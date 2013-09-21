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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


def url_callback(url, pass_through_kwargs):
    """
    A quick shortcut for passing kwargs in the current request context to the URLs we want to generate.

    This assumes the naming of kwargs to be consistent across pages.

    A list of kwargs to be passed through must be provided. Remember, if we provide too many kwargs the
    URL lookup will fail.

    """

    def lazy(context):
        pass_through = {}

        for kwarg in pass_through_kwargs:
            pass_through[kwarg] = context['request'].resolver_match.kwargs[kwarg]

        return reverse(url, kwargs=pass_through)

    return lazy


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
              'url_callback': url_callback('sadmin2:event_overview', ('event_pk',)),
              'parent': 'events'},

    # Assumes: context[event], kwargs[event_pk]
    'event_attendees':  {
        'name': _('Attendees'),
        'url_callback': url_callback('sadmin2:event_attendees', ('event_pk',)),
        'parent': 'event'},

    # Assumes: context[event], kwargs[event_pk]
    'event_attendees_add':  {
        'name': _('Add user'),
        'url_callback': url_callback('sadmin2:event_attendees_add', ('event_pk',)),
        'parent': 'event_attendees'},

    # Assumes: context[event], kwargs[event_pk]
    'event_account':  {
        'name': _('Account'),
        'url_callback': url_callback('sadmin2:event_account', ('event_pk',)),
        'parent': 'event'},

    # Assumes: context[event], kwargs[event_pk]
    'event_settings':  {
        'name': _('Settings'),
        'url_callback': url_callback('sadmin2:event_settings', ('event_pk',)),
        'parent': 'event'},

    # Assumes: context[event], kwargs[event_pk]
    'event_selections':  {
        'name': _('Selections'),
        'url_callback': url_callback('sadmin2:event_selections', ('event_pk',)),
        'parent': 'event'},

    # Assumes: context[event], kwargs[event_pk]
    'event_selections_create_group':  {
        'name': _('Create Group'),
        'url_callback': url_callback('sadmin2:event_selections_create_group', ('event_pk',)),
        'parent': 'event_selections'},

    # Assumes: context[event], context[option_group], kwargs[event_pk]
    'event_selections_group':  {
        'name_callback': lambda context: context['option_group'].name,
        'url_callback': url_callback('sadmin2:event_selections', ('event_pk',)),
        'parent': 'event_selections'},

    # Assumes: context[event], context[option_group], kwargs[event_pk], kwargs[group_pk]
    'event_selections_edit_group':  {
        'name': _('Edit'),
        'url_callback': url_callback('sadmin2:event_selections_edit_group', ('event_pk', 'group_pk')),
        'parent': 'event_selections_group'},

    # Assumes: context[event], kwargs[event_pk]
    'event_selections_create_option':  {
        'name': _('Create Option'),
        'url_callback': url_callback('sadmin2:event_selections_create_option', ('event_pk', 'group_pk')),
        'parent': 'event_selections_group'},

    # Assumes: context[event], context[option_group], context[option],
    #          kwargs[event_pk], kwargs[group_pk], kwargs[option_pk]
    'event_selections_edit_option':  {
        'name_callback': lambda context: context['option'].name,
        'url_callback': url_callback('sadmin2:event_selections_edit_option', ('event_pk', 'group_pk', 'option_pk')),
        'parent': 'event_selections_group'},

    # Assumes: context[event], kwargs[event_pk]
    'event_report_registration':  {
        'name': _('Registration history'),
        'url_callback': url_callback('sadmin2:event_report_registration', ('event_pk',)),
        'parent': 'event'},

    # Assumes: context[event], kwargs[event_pk]
    'event_report_check_in':  {
        'name': _('Check-in history'),
        'url_callback': url_callback('sadmin2:event_report_check_in', ('event_pk',)),
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
    {'id': 'overview',
     'name': _('Overview'),
     'url_callback': url_callback('sadmin2:event_overview', ('event_pk',))},

    {'id': 'attendees',
     'name': u'Deltagere',
     'url_callback': url_callback('sadmin2:event_attendees', ('event_pk',))},

    {'id': 'selections',
     'name': u'Tilvalg',
     'url_callback': url_callback('sadmin2:event_selections', ('event_pk',))},

    {'id': 'reports',
     'name': _('Reports'),
     'dropdown': (
         {'id': 'reports-account',
          'name': _('Account'),
          'url_callback': url_callback('sadmin2:event_account', ('event_pk',))},

         {'id': 'reports-registration-history',
          'name': _('Registration history'),
          'url_callback': url_callback('sadmin2:event_report_registration', ('event_pk',))},

         {'id': 'reports-checkin-history',
          'name': _('Check-in history'),
          'url_callback': url_callback('sadmin2:event_report_check_in', ('event_pk',))}

     )},

    {'id': 'settings',
     'name': u'Settings',
     'url_callback': url_callback('sadmin2:event_settings', ('event_pk',))
     }
)


sadmin2_menu_manifest = {
    'sadmin2_menu_main': sadmin2_menu_main
}
