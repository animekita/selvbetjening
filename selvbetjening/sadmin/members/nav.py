from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from selvbetjening.sadmin.base import nav

nav.registry['main'].register(nav.Option(_('Members'), 'sadmin:members_list'))

# members menu
members_menu = nav.Navigation()
nav.registry['members'] = members_menu

members_menu.register(nav.Option(_(u'Find Member'), 'sadmin:members_list'))
members_menu.register(nav.Option(_(u'Create Member'), 'sadmin:members_create'))

# member menu
member_menu = nav.Navigation()
nav.registry['member'] = member_menu

member_menu.register(nav.Option(_(u'Personal Information'),
    lambda ctx: reverse('sadmin:members_view', kwargs={'username': ctx['user'].username})))

member_menu.register(nav.Option(_(u'Access Control'),
    lambda ctx: reverse('sadmin:members_view_access', kwargs={'username': ctx['user'].username})))