from django.conf import settings
from django.conf.urls import *

from selvbetjening.portal.profile.views import profile_redirect

urlpatterns = patterns('',
    url(r'^$', profile_redirect, name='home'),

    (r'^profil/', include('selvbetjening.portal.profile.urls')),

    (r'^bliv-medlem/', include('selvbetjening.portal.quickregistration.urls')),
    (r'^events/', include('selvbetjening.portal.eventregistration.urls')),

    (r'^sadmin2/', include('selvbetjening.sadmin2.urls', namespace='sadmin2')),

    (r'^api/sso/', include('selvbetjening.api.sso.urls')),

)

if getattr(settings, 'STATIC_DEBUG', False):
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
    )
