# coding=utf-8

from django.utils.translation import ugettext_lazy as _

"""

    Breadcrumbs

    A breadcrumb consist of a sequence of items, each rendered as a link to a page in sadmin2.

    For each unique sequence you will need to add an entry to the breadcrumbs dictionary. The
    sequence will be calculated by following the entry's parent pointer recursively.

    Rendering and recursive traversal of the breadcrumbs are handled by the sadmin2_breadcrumbs
    template tag.

    Each entry consists of an ID (the key) referenced by the parent properties, and a
    dictionary with the following keys.

    name (required): The label rendered to the page
    url (required): A string resolvable to a URL if used in the {% url %} template tag
    parent (optional): A string pointing to an existing parent entry.
                       The traversal stops if this value is None or omitted.


"""

breadcrumbs = {
    'dashboard': {'name': _('Dashboard'), 'url': 'sadmin2:dashboard'},
    'events': {'name': _('Events'), 'url': 'sadmin2:events_list', 'parent': 'dashboard'}
}

sadmin2_menu_main = (
    {'id': 'events', 'name': _('Events'), 'url': 'sadmin2:events_list'},
    {'id': 'users', 'name': _('Users'), 'url': 'sadmin:auth_user_changelist'},
    {'id': 'emails', 'name': _('Newsletters'), 'url': 'sadmin:mailcenter_emailspecification_changelist'}
)

sadmin2_menu_event = (
    {'items': (
        {'id': 'attendees', 'name': u'Deltagere', 'url': 'sadmin2:events_attendees_list', 'icon': 'group'},
        {'id': 'statistics', 'name': u'Statistik', 'url': 'sadmin2:events_statistics', 'icon': 'picture'},
        {'id': 'financial', 'name': u'Økonomi', 'url': 'sadmin2:events_financial', 'icon': 'money'},
        {'id': 'settings', 'name': u'Settings', 'icon': 'wrench', 'dropdown': (
            {'id': 'settings-event', 'name': u'Arrangement', 'url': 'sadmin2:events_settings'},
            {'id': 'settings-selections', 'name': u'Tilvalg', 'url': 'sadmin2:events_settings_selections'}
        )}

    )}
)

sadmin2_menu_manifest = {
    'sadmin2_menu_main': sadmin2_menu_main,
    'sadmin2_menu_event': sadmin2_menu_event
}
