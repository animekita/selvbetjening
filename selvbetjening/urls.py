from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to, direct_to_template

from selvbetjening.core.views import frontpage

urlpatterns = patterns('',
    url(r'^$', frontpage, name='home'),

    (r'^profil/', include('selvbetjening.members.urls')),
    (r'^bliv-medlem/', include('selvbetjening.quickregistration.urls')),
    (r'^events/', include('selvbetjening.events.urls')),
    (r'^accounting/', include('selvbetjening.accounting.urls')),
    (r'^booking/', include('selvbetjening.booking.urls')),
    (r'^mailcenter/', include('selvbetjening.mailcenter.urls')),

    # Admin urls
    (r'^admin/', include('selvbetjening.mailcenter.admin_urls')),
    (r'^admin/', include('selvbetjening.events.admin_urls')),
    (r'^admin/', include('selvbetjening.accounting.admin_urls')),

    (r'^eventadmin/', include('selvbetjening.eventmode.urls')),
)