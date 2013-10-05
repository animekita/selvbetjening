from django.conf import settings
from django.conf.urls import *

from selvbetjening.portal.profile.views import profile_redirect

from selvbetjening.sadmin.base import sadmin
from selvbetjening.sadmin.members.models import MembersRootAdmin
from selvbetjening.sadmin.events.models import EventsRootAdmin
from selvbetjening.sadmin.mailcenter.models import MailcenterRootAdmin

sadmin.site.register('members', MembersRootAdmin)
sadmin.site.register('events', EventsRootAdmin)
sadmin.site.register('mailcenter', MailcenterRootAdmin)

urlpatterns = patterns('',
    url(r'^$', profile_redirect, name='home'),

    (r'^profil/', include('selvbetjening.portal.profile.urls')),

    (r'^bliv-medlem/', include('selvbetjening.portal.quickregistration.urls')),
    (r'^events/', include('selvbetjening.portal.eventregistration.urls')),

    (r'^sadmin/', include(sadmin.site.urls)),
    (r'^sadmin2/', include('selvbetjening.sadmin2.urls', namespace='sadmin2')),

    (r'^api/sso/', include('selvbetjening.api.sso.urls')),

)

if getattr(settings, 'STATIC_DEBUG', False):
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
    )
