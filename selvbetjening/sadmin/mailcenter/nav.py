from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from selvbetjening.sadmin.base import nav

# mailcenter submenu
mailcenter_menu = nav.Navigation(_('Mailcenter'))
nav.registry['main'].register(mailcenter_menu)

mailcenter_menu.register(nav.Option(_(u'Browse E-mails'), 'sadmin:mailcenter_emails_list',
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

mailcenter_menu.register(nav.Option(_(u'Create E-mail Draft'), 'sadmin:mailcenter_emails_create',
    lambda user: user.has_perm('mailcenter.add_emailspecification'))
)

# email menu
email_menu = nav.Navigation()
nav.registry['email'] = email_menu

email_menu.register(nav.Option(_(u'Update'),
    lambda ctx: reverse('sadmin:mailcenter_email_update', kwargs={'email_pk': ctx['email'].pk}),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

email_menu.register(nav.Option(_(u'Preview'),
    lambda ctx: reverse('sadmin:mailcenter_email_preview', kwargs={'email_pk': ctx['email'].pk}),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

email_menu.register(nav.Option(_(u'Send'),
    lambda ctx: reverse('sadmin:mailcenter_email_send', kwargs={'email_pk': ctx['email'].pk}),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

email_menu.register(nav.Option(_(u'Bind to Event'),
    lambda ctx: reverse('sadmin:mailcenter_email_bind', kwargs={'email_pk': ctx['email'].pk}),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)

email_menu.register(nav.Option(_(u'Filters'),
    lambda ctx: reverse('sadmin:mailcenter_email_filter', kwargs={'email_pk': ctx['email'].pk}),
    lambda user: user.has_perm('mailcenter.change_emailspecification'))
)