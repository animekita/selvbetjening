from django.conf.urls import *
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from selvbetjening.sadmin.base.nav import RemoteSPage
from selvbetjening.scheckin import views

urlpatterns = patterns('',
    url(r'^(?P<event_id>[0-9]+)/$', views.checkin, name='scheckin_checkin'),
)

if 'selvbetjening.sadmin.events' in settings.INSTALLED_APPS:
    import selvbetjening.sadmin.base.sadmin

    scheckin_url = lambda context, stack: reverse('scheckin_checkin', kwargs={'event_id': stack[-1].pk})
    scheckin_page = RemoteSPage(_(u'Now Check-in'), scheckin_url)

    selvbetjening.sadmin.base.sadmin.site.get('events').attendee_admin.sadmin_action_menu.register(scheckin_page)