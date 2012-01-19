from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to, direct_to_template

from selvbetjening.sadmin.base import sadmin
from selvbetjening.portal.profile.views import profile_redirect

urlpatterns = patterns('',
    url(r'^$', profile_redirect, name='home'),

    (r'^profil/',
     include('selvbetjening.core.members.urls')),

    (r'^bliv-medlem/',
     include('selvbetjening.portal.quickregistration.urls')),

    (r'^events/',
     include('selvbetjening.portal.eventregistration.urls')),

    (r'^api/',
     include('selvbetjening.api.sso.urls')),

    (r'^api/',
     include('selvbetjening.api.eventsapi.urls')),

    (r'^notify/vanillaforum/',
     include('selvbetjening.notify.vanillaforum.urls')),

    # Admin urls
    (r'^admin/', include(sadmin.site.urls)),
)