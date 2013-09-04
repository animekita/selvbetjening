# coding=utf-8


sadmin2_menu = (
    {'name': u'Arrangementer',
     'items': (
         {'name': u'Browse', 'url': 'sadmin2:events_list'},
         {'name': u'Registrer betalinger', 'url': 'sadmin:events_event_register_payment'},
     )},
    {'name': u'Brugere',
     'items': (
         {'name': u'Browse', 'url': 'sadmin:auth_user_changelist'},
         {'name': u'Statistik', 'url': 'sadmin:auth_user_statistics'},
         {'name': u'Rettigheder', 'url': 'sadmin:auth_group_changelist'},
     )},
    {'name': u'E-mails',
     'items': (
         {'name': u'Nyhedsbreve', 'url': 'sadmin:mailcenter_emailspecification_changelist'},
         {'name': u'Skabeloner', 'url': 'sadmin:mailcenter_emailspecification_changelist'},
         {'name': u'Udgående kø', 'url': 'sadmin:mailer_message_changelist'},
     )},
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
    'sadmin2_menu_main': sadmin2_menu,
    'sadmin2_menu_event': sadmin2_menu_event
}
