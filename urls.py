from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^$',
        direct_to_template,
        {'template' : 'index.html'},
        name = 'home'),
    
    (r'^', include('kita-site.members.urls')),
    (r'^events/', include('kita-site.events.urls')),

    # Admin urls
    (r'^admin/', include('django.contrib.admin.urls')),
)
