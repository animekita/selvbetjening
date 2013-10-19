from django.conf import settings
from django.conf.urls import *

from django.views.generic.base import TemplateView

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='demo/index.html'), name='home'),

    (r'^auth/', include('selvbetjening.frontend.auth.urls')),
    (r'^userportal/', include('selvbetjening.frontend.userportal.urls')),
    (r'^eventportal/', include('selvbetjening.frontend.eventportal.urls')),
    (r'^eventsingle/', include('selvbetjening.frontend.eventsingle.urls')),

    (r'^%s/' % settings.SADMIN2_BASE_URL, include('selvbetjening.sadmin2.urls', namespace='sadmin2')),

    (r'^api/sso/', include('selvbetjening.api.sso.urls')),

)

if getattr(settings, 'STATIC_DEBUG', False):
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
    )
