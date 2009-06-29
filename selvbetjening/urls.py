from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to, direct_to_template

from selvbetjening.core.views import frontpage
from selvbetjening.clients.profile.views import profile

urlpatterns = patterns('',
    url(r'^$', frontpage, name='home'),

    (r'^profil/', 
     include('selvbetjening.data.members.urls')),
    
    (r'^bliv-medlem/', 
     include('selvbetjening.clients.quickregistration.urls')),
    
    (r'^events/', 
     include('selvbetjening.data.events.urls')),
    
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