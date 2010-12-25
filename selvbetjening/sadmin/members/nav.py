from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from selvbetjening.sadmin.base import nav

# main menu
main_menu = nav.Navigation(_('Members'))
nav.registry['main'].register(main_menu)

main_menu.register(nav.Option(_(u'Browse Members'), 'sadmin:members_user_changelist',
    lambda user: user.has_perm('auth.change_user'))
)

main_menu.register(nav.Option(_(u'Browse Groups'), 'sadmin:members_group_changelist',
    lambda user: user.has_perm('auth.change_user'))
)

# browse members menu
members_menu = nav.Navigation()

members_menu.register(nav.Option(_(u'Browse Members'),
    'sadmin:members_user_changelist',
    lambda user: user.has_perm('auth.change_user'))
)

members_menu.register(nav.Option(_(u'Create Member'),
    'sadmin:members_user_add',
    lambda user: user.has_perm('auth.create_user'))
)

members_menu.register(nav.Option(_(u'Browse Groups'),
    'sadmin:members_group_changelist',
    lambda user: user.has_perm('auth.change_user'))
)

members_menu.register(nav.Option(_(u'Create Group'),
    'sadmin:members_group_add',
    lambda user: user.has_perm('auth.create_user'))
)

members_menu.register(nav.Option(_(u'Statistics'),
    'sadmin:members_user_statistics',
    lambda user: user.has_perm('auth.create_user'))
)

# member menu
member_menu = nav.Navigation()

member_menu.register(nav.Option(_(u'Personal Information'),
    lambda ctx: reverse('sadmin:members_user_change', args=[ctx['username']]),
    lambda user: user.has_perm('auth.change_user'))
)

member_menu.register(nav.Option(_(u'Change Password'),
    lambda ctx: reverse('sadmin:members_user_change_password', kwargs={'username': ctx['username']}),
    lambda user: user.has_perm('auth.change_user'))
)