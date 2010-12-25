from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from selvbetjening.sadmin.base import nav

# mailcenter submenu
mailcenter_menu = nav.Navigation(_('Mailcenter'))
nav.registry['main'].register(mailcenter_menu)

mailcenter_menu.register(nav.Option(_(u'Browse E-mails'),
    'sadmin:mailcenter_emailspecification_changelist',
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

mailcenter_menu.register(nav.Option(_(u'Outgoing e-mails'), 
    'sadmin:mailcenter_outgoing_changelist',
    lambda user: user.has_perm('mailcenter.add_emailspecification'))
)

# emails menu

emails_menu = nav.Navigation()

emails_menu.register(nav.Option(_(u'Browse e-mails'),
    lambda ctx: reverse('sadmin:mailcenter_emailspecification_changelist'),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

emails_menu.register(nav.Option(_(u'Outgoing e-mails'),
    lambda ctx: reverse('sadmin:mailcenter_outgoing_changelist'),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

emails_menu.register(nav.Option(_(u'Create E-mail Draft'),
    'sadmin:mailcenter_emailspecification_add',
    lambda user: user.has_perm('mailcenter.add_emailspecification'))
)

# email menu
email_menu = nav.Navigation()

email_menu.register(nav.Option(_(u'Email'),
    lambda ctx: reverse('sadmin:mailcenter_emailspecification_change', args=[ctx['email_pk']]),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

email_menu.register(nav.Option(_(u'Filters'),
    lambda ctx: reverse('sadmin:mailcenter_emailspecification_change_filter', kwargs={'email_pk': ctx['email_pk']}),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

email_menu.register(nav.Option(_(u'Send'),
    lambda ctx: reverse('sadmin:mailcenter_emailspecification_send', kwargs={'email_pk': ctx['email_pk']}),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

email_menu.register(nav.Option(_(u'Mass E-email'),
    lambda ctx: reverse('sadmin:mailcenter_emailspecification_masssend', kwargs={'email_pk': ctx['email_pk']}),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)