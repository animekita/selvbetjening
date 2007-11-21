from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.core.urlresolvers import reverse

urlpatterns = patterns('',
    url(r'^$',
        redirect_to,
        {'url' : '/login/'},
        name = 'home'),
    
    (r'^', include('kita-site.members.urls')),
    (r'^events/', include('kita-site.events.urls')),
    (r'^migrate/', include('kita-site.migration.urls')),

    # Admin urls
    (r'^admin/', include('django.contrib.admin.urls')),
)
