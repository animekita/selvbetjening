from django.conf import settings
from django.conf.urls import *

from selvbetjening.portal.profile.views import profile_redirect
from selvbetjening.sadmin.base import sadmin

# workaround for missing urls
from selvbetjening.sadmin.events import models as event_models
from selvbetjening.sadmin.mailcenter import models as mail_models
from selvbetjening.sadmin.members import models as members_models

urlpatterns = patterns('',
    url(r'^$', profile_redirect, name='home'),

    (r'^profil/opdater/forum/', include('selvbetjening.notify.vanillaforum.urls')),
    (r'^profil/', include('selvbetjening.portal.profile.urls')),

    (r'^bliv-medlem/', include('selvbetjening.portal.quickregistration.urls')),
    (r'^events/', include('selvbetjening.portal.eventregistration.urls')),

    (r'^sadmin/', include(sadmin.site.urls)),

    (r'^api/sso/', include('selvbetjening.api.sso.urls')),
    (r'^api/rest/', include('selvbetjening.api.rest.urls')),

    (r'^scheckin/now/', include('selvbetjening.scheckin.easy.urls')),

)

if getattr(settings, 'STATIC_DEBUG', False):
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
    )
