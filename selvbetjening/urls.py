from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to, direct_to_template

from selvbetjening.clients.profile.views import profile, profile_redirect

urlpatterns = patterns('',
    url(r'^$', profile_redirect, name='home'),

    (r'^profil/', 
     include('selvbetjening.data.members.urls')),
    
    (r'^bliv-medlem/', 
     include('selvbetjening.clients.quickregistration.urls')),
    
    (r'^events/', 
     include('selvbetjening.clients.eventregistration.urls')),
    
    (r'^accounting/', 
     include('selvbetjening.data.accounting.urls')),
    
    (r'^mailcenter/', 
     include('selvbetjening.clients.mailcenter.urls')),
    
    url(r'^profil/$', profile, name='members_profile'),
    
    # Admin urls
    (r'^admin/', include('selvbetjening.clients.mailcenter.admin_urls')),
    (r'^admin/', include('selvbetjening.data.events.admin_urls')),
    (r'^admin/', include('selvbetjening.data.accounting.admin_urls')),

    (r'^eventadmin/', include('selvbetjening.clients.eventmode.urls')),
)