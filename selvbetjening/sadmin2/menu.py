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
    hide (optional): callback taking the context as an argument. If it returns true then the item will not be rendered.


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

    'users': {'name': _('Users'),
              'url': 'sadmin2:users_list'},

    'users_create': {'name': _('Create'),
                     'url': 'sadmin2:users_create',
                     'parent': 'users'},

    'users_groups': {'name': _('Groups'),
                     'url': 'sadmin2:users_groups_list',
                     'parent': 'users'},

    'users_groups_create': {'name': _('Create'),
                            'url': 'sadmin2:users_groups_create',
                            'parent': 'users_groups'},

    'users_reports': {'name': _('Reports'),
                      'parent': 'users'},

    'users_reports_age': {'name': _('Age'),
                          'url': 'sadmin2:users_reports_age',
                          'parent': 'users_reports'},

    'users_reports_users': {'name': _('Users'),
                            'url': 'sadmin2:users_reports_users',
                            'parent': 'users_reports'},

    'users_reports_address': {'name': _('Address'),
                              'url': 'sadmin2:users_reports_address',
                              'parent': 'users_reports'},

    # Assumes: context[group], kwargs[group_pk]
    'users_group': {'name_callback': lambda context: context['group'].name,
                    'url_callback': url_callback('sadmin2:users_group', ('group_pk',)),
                    'parent': 'users_groups'},

    # Assumes: context[user], kwargs[user_pk]
    'user': {'name_callback': lambda context: context['user'].username,
             'url_callback': url_callback('sadmin2:user', ('user_pk',)),
             'parent': 'users'},

    # Assumes: context[user], kwargs[user_pk]
    'user_password': {'name': _('Password'),
                      'url_callback': url_callback('sadmin2:user_password', ('user_pk',)),
                      'parent': 'user'},

    'events': {'name': _('Events'),
               'url': 'sadmin2:events_list'},

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

    # Assumes: context[event], context[attendee], kwargs[event_pk], kwargs[attendee_pk]
    'event_attendees_attendee':  {
        'name_callback': lambda context: context['attendee'].user.username,
        'url_callback': url_callback('sadmin2:event_attendee', ('event_pk', 'attendee_pk')),
        'parent': 'event_attendees'},

    # Assumes: context[event], context[attendee], kwargs[event_pk], kwargs[attendee_pk]
    'event_attendees_attendee_payments':  {
        'name': _('Payments'),
        'url_callback': url_callback('sadmin2:event_attendee_payments', ('event_pk', 'attendee_pk')),
        'parent': 'event_attendees_attendee'},

    # Assumes: context[event], context[attendee], kwargs[event_pk], kwargs[attendee_pk]
    'event_attendees_attendee_selections':  {
        'name': _('Selections'),
        'url_callback': url_callback('sadmin2:event_attendee_selections', ('event_pk', 'attendee_pk')),
        'parent': 'event_attendees_attendee'},

    # Assumes: context[event], context[attendee], kwargs[event_pk], kwargs[attendee_pk]
    'event_attendees_attendee_notes':  {
        'name': _('Notes'),
        'url_callback': url_callback('sadmin2:event_attendee_notes', ('event_pk', 'attendee_pk')),
        'parent': 'event_attendees_attendee'},

    # Assumes: context[event], context[attendee], kwargs[event_pk], kwargs[attendee_pk]
    'event_attendees_attendee_delete':  {
        'name': _('Delete'),
        'url_callback': url_callback('sadmin2:event_attendee_delete', ('event_pk', 'attendee_pk')),
        'parent': 'event_attendees_attendee'},

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
    'event_settings_selections':  {
        'name': _('Selections'),
        'url_callback': url_callback('sadmin2:event_settings_selections', ('event_pk',)),
        'parent': 'event_settings'},

    # Assumes: context[event], kwargs[event_pk]
    'event_selections_create_group':  {
        'name': _('Create Group'),
        'url_callback': url_callback('sadmin2:event_selections_create_group', ('event_pk',)),
        'parent': 'event_settings_selections'},

    # Assumes: context[event], context[option_group], kwargs[event_pk]
    'event_selections_group':  {
        'name_callback': lambda context: context['option_group'].name if context['option_group'].name != '' else 'anon',
        'url_callback': url_callback('sadmin2:event_settings_selections', ('event_pk',)),
        'parent': 'event_settings_selections'},

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
    'event_selections_option':  {
        'name_callback': lambda context: context['option'].name,
        'url_callback': url_callback('sadmin2:event_selections_edit_option', ('event_pk', 'group_pk', 'option_pk')),
        'parent': 'event_selections_group'},

    # Assumes: context[event], context[option_group], context[option],
    #          kwargs[event_pk], kwargs[group_pk], kwargs[option_pk]
    'event_selections_edit_option':  {
        'name': _('Edit'),
        'url_callback': url_callback('sadmin2:event_selections_edit_option', ('event_pk', 'group_pk', 'option_pk')),
        'parent': 'event_selections_option'},

    # Assumes: context[event], context[option_group], context[option],
    #          kwargs[event_pk], kwargs[group_pk], kwargs[option_pk]
    'event_selections_delete_option':  {
        'name': _('Delete'),
        'url_callback': url_callback('sadmin2:event_selections_delete_option', ('event_pk', 'group_pk', 'option_pk')),
        'parent': 'event_selections_option'},

    # Assumes: context[event], kwargs[event_pk]
    'event_selections':  {
        'name': _('Selections'),
        'url_callback': url_callback('sadmin2:event_selections', ('event_pk',)),
        'parent': 'event'},

    # Assumes: context[event], kwargs[event_pk]
    'event_selections_transfer':  {
        'name': _('Transfer'),
        'url_callback': url_callback('sadmin2:event_selections_transfer', ('event_pk',)),
        'parent': 'event_selections'},

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

    # Assumes: context[event], kwargs[event_pk]
    'event_report_age':  {
        'name': _('Attendee age'),
        'url_callback': url_callback('sadmin2:event_report_age', ('event_pk',)),
        'parent': 'event'},

    # Assumes: context[event], kwargs[event_pk]
    'event_report_address':  {
        'name': _('Attendee addresses'),
        'url_callback': url_callback('sadmin2:event_report_address', ('event_pk',)),
        'parent': 'event'},

    'emails': {
        'name': _('E-mails')
    },

    'emails_queue': {
        'name': _('Delivery Log'),
        'url': 'sadmin2:emails_queue',
        'parent': 'emails'
    },

    'emails_templates': {
        'name': _('Templates'),
        'url': 'sadmin2:emails_templates',
        'parent': 'emails'
    },

    'emails_templates_create': {
        'name': _('Create'),
        'url': 'sadmin2:emails_templates_create',
        'parent': 'emails_templates'
    },

    # Assumes: context[template], kwargs[template_pk]
    'emails_template': {
        'name_callback': lambda context: context['template'].subject,
        'url_callback': url_callback('sadmin2:emails_template', ('template_pk',)),
        'parent': 'emails_templates'
    },

    # Assumes: context[template], kwargs[template_pk]
    'emails_template_preview': {
        'name': _('Preview'),
        'url_callback': url_callback('sadmin2:emails_template_preview', ('template_pk',)),
        'parent': 'emails_template'
    },

    # Assumes: context[template], kwargs[template_pk]
    'emails_template_send': {
        'name': _('Send'),
        'url_callback': url_callback('sadmin2:emails_template_send', ('template_pk',)),
        'parent': 'emails_template'
    },

    # Assumes: context[template], kwargs[template_pk]
    'emails_template_newsletter_users': {
        'name': _('User Newsletter'),
        'url_callback': url_callback('sadmin2:emails_template_newsletter_users', ('template_pk',)),
        'parent': 'emails_template'
    },

    # Assumes: context[template], kwargs[template_pk]
    'emails_template_newsletter_attendees': {
        'name': _('Event Newsletter'),
        'url_callback': url_callback('sadmin2:emails_template_newsletter_attendees', ('template_pk',)),
        'parent': 'emails_template'
    }
}

sadmin2_menu_tab_events = (
    {'id': 'events', 'name': _('Events'), 'url': 'sadmin2:events_list'},
    {'id': 'events_register_payments', 'name': _('Register Payment'), 'url': 'sadmin2:events_register_payments'}
)

sadmin2_menu_tab_users = (
    {'id': 'users', 'name': _('Users'), 'url': 'sadmin2:users_list'},
    {'id': 'groups', 'name': _('Groups'), 'url': 'sadmin2:users_groups_list'},

    {'id': 'reports',
     'name': _('Reports'),
     'dropdown': (
         {'id': 'reports-users',
          'name': _('Users'),
          'url_callback': url_callback('sadmin2:users_reports_users', ())},

         {'id': 'reports-age',
          'name': _('Age'),
          'url_callback': url_callback('sadmin2:users_reports_age', ())},

         {'id': 'reports-address',
          'name': _('Map'),
          'url_callback': url_callback('sadmin2:users_reports_address', ())},
     )}
)

sadmin2_menu_tab_user = (
    {'id': 'user',
     'name': _('User'),
     'url_callback': url_callback('sadmin2:user', ('user_pk', ))},
    {'id': 'password',
     'name': _('Password'),
     'url_callback': url_callback('sadmin2:user_password', ('user_pk', ))}
)

sadmin2_menu_tab_attendee = (
    {'id': 'registration',
     'name': _('Registration'),
     'url_callback': url_callback('sadmin2:event_attendee', ('event_pk', 'attendee_pk'))},

    {'id': 'selections',
     'name': _('Selections'),
     'url_callback': url_callback('sadmin2:event_attendee_selections', ('event_pk', 'attendee_pk'))},

    {'id': 'payments',
     'name': _('Payments'),
     'url_callback': url_callback('sadmin2:event_attendee_payments', ('event_pk', 'attendee_pk'))},

    {'id': 'notes',
     'name_callback': lambda context: _('Notes %s') % ('<span class="badge">%s<span>' % context['attendee'].comments.count()),
     'url_callback': url_callback('sadmin2:event_attendee_notes', ('event_pk', 'attendee_pk'))},

    {'id': 'back-to-event',
     'name': _('Back to event'),
     'url_callback': url_callback('sadmin2:event_attendees', ('event_pk',)),
     'class': 'pull-right',
     'icon': 'arrow-left'},

    {'id': 'to-user-account',
     'name': _('User account'),
     'url_callback': lambda context: reverse('sadmin2:user', kwargs={'user_pk': context['attendee'].user.pk}),
     'class': 'pull-right',
     'icon': 'user'},

    {'id': 'delete',
     'name': _('Delete'),
     'url_callback': url_callback('sadmin2:event_attendee_delete', ('event_pk', 'attendee_pk')),
     'class': 'pull-right',
     'icon': 'trash'}


)

# Assumes kwargs[event_pk]
sadmin2_menu_tab_event = (
    {'id': 'overview',
     'name': _('Overview'),
     'url_callback': url_callback('sadmin2:event_overview', ('event_pk',))},

    {'id': 'attendees',
     'name': _(u'Attendees'),
     'url_callback': url_callback('sadmin2:event_attendees', ('event_pk',))},

    {'id': 'selections',
     'name': _(u'Selections'),
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
          'url_callback': url_callback('sadmin2:event_report_check_in', ('event_pk',))},

         {'id': 'reports-age',
          'name': _('Attendee age'),
          'url_callback': url_callback('sadmin2:event_report_age', ('event_pk',))},

         {'id': 'reports-address',
          'name': _('Map'),
          'url_callback': url_callback('sadmin2:event_report_address', ('event_pk',))}

     )},

    {'id': 'settings',
     'name': _('Settings'),
     'dropdown': (

         {'id': 'settings_event',
          'name': _(u'Event'),
          'url_callback': url_callback('sadmin2:event_settings', ('event_pk',))
          },

         {'id': 'settings_selections',
          'name': _(u'Selections'),
          'url_callback': url_callback('sadmin2:event_settings_selections', ('event_pk',))
          }

     )}
)

sadmin2_menu_tab_emails = (
    {
        'id': 'templates',
        'name': _('Templates'),
        'url': 'sadmin2:emails_templates'
    },

    {
        'id': 'queue',
        'name': _('Delivery Log'),
        'url': 'sadmin2:emails_queue'
    }

)

sadmin2_menu_tab_template = (
    {
        'id': 'template',
        'name': _('Template'),
        'url_callback': url_callback('sadmin2:emails_template', ('template_pk',))
    },

    {
        'id': 'preview',
        'name': _('Preview'),
        'url_callback': url_callback('sadmin2:emails_template_preview', ('template_pk',))
    },

    {
        'id': 'send',
        'name': _('Send'),
        'dropdown': (
            {
                'id': 'send-single',
                'name': _('Direct to User'),
                'url_callback': url_callback('sadmin2:emails_template_send', ('template_pk',))
            },

            {
                'id': 'send-newsletter-user',
                'name': _('User Newsletter'),
                'url_callback': url_callback('sadmin2:emails_template_newsletter_users', ('template_pk',)),
                'hide': lambda context: context['template'].template_context == 'attendee'
            },

            {
                'id': 'send-newsletter-attendees',
                'name': _('Event Newsletter'),
                'url_callback': url_callback('sadmin2:emails_template_newsletter_attendees', ('template_pk',)),
            }
        )
    }
)

sadmin2_menu_main = (
    {'id': 'users',
     'name': _('Users'),
     'url': 'sadmin2:users_list'},
    {'id': 'events',
     'name': _('Events'),
     'url': 'sadmin2:events_list'},
    {'id': 'emails',
     'name': _('E-mails'),
     'url': 'sadmin2:emails_templates'}
)

sadmin2_menu_manifest = {
    'sadmin2_menu_main': sadmin2_menu_main
}
