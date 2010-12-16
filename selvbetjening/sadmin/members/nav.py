from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from selvbetjening.sadmin.base import nav

# members menu
members_menu = nav.Navigation(_('Members'))
nav.registry['main'].register(members_menu)

members_menu.register(nav.Option(_(u'Browse Members'), 'sadmin:members_user_changelist',
    lambda user: user.has_perm('auth.change_user'))
)

members_menu.register(nav.Option(_(u'Browse Groups'), 'sadmin:members_group_changelist',
    lambda user: user.has_perm('auth.change_user'))
)

# browse members menu
browse_members_menu = nav.Navigation()

browse_members_menu.register(nav.Option(_(u'Browse Members'),
    'sadmin:members_user_changelist',
    lambda user: user.has_perm('auth.change_user'))
)

browse_members_menu.register(nav.Option(_(u'Create Member'),
    'sadmin:members_user_add',
    lambda user: user.has_perm('auth.create_user'))
)

browse_members_menu.register(nav.Option(_(u'Statistics'),
    'sadmin:members_user_statistics',
    lambda user: user.has_perm('auth.create_user'))
)

# browse group menu
browse_group_menu = nav.Navigation()

browse_group_menu.register(nav.Option(_(u'Browse Groups'),
    'sadmin:members_group_changelist',
    lambda user: user.has_perm('auth.change_user'))
)

browse_group_menu.register(nav.Option(_(u'Create Group'),
    'sadmin:members_group_add',
    lambda user: user.has_perm('auth.create_user'))
)

# member menu
member_menu = nav.Navigation()

member_menu.register(nav.Option(_(u'Personal Information'),
    lambda ctx: reverse('sadmin:members_view', kwargs={'username': ctx['username']}),
    lambda user: user.has_perm('auth.change_user'))
)