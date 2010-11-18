from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from selvbetjening.sadmin.base import nav

# members menu
members_menu = nav.Navigation(_('Members'))
nav.registry['main'].register(members_menu)

members_menu.register(nav.Option(_(u'Browse Members'), 'sadmin:members_list',
    lambda user: user.has_perm('auth.change_user'))
)

members_menu.register(nav.Option(_(u'Create Member'), 'sadmin:members_create',
    lambda user: user.has_perm('auth.create_user'))
)

# member menu
member_menu = nav.Navigation()
nav.registry['member'] = member_menu

member_menu.register(nav.Option(_(u'Personal Information'),
    lambda ctx: reverse('sadmin:members_view', kwargs={'username': ctx['user'].username}),
    lambda user: user.has_perm('auth.change_user'))
)

member_menu.register(nav.Option(_(u'Access Control'),
    lambda ctx: reverse('sadmin:members_view_access', kwargs={'username': ctx['user'].username}),
    lambda user: user.has_perm('auth.change_user'))
)