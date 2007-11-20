from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('migration.views',  
    url(r'^forum/$',
        "vanillaforum",
        name='migrate_vanillaforum'),
    
    url(r'^forum/ny-bruger/$',
        "vanillaforumStep2",
        name='migrate_vanillaforum_step2'),
    
    url(r'^forum/ny-bruger/done/$',
        direct_to_template,
        {"template" : "migration/vanillaforumDone.html"},
        name='migrate_vanillaforum_done'),
)