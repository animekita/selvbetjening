from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to, direct_to_template
from django.contrib.auth import views as auth_views
from django.contrib import admin

from core.views import frontpage

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',
        frontpage,
        name = 'home'),

    url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html'},
        name='auth_login'),

    url(r'^logud/$',
        auth_views.logout,
        {'template_name': 'registration/logout.html', 'next_page' : '/login/'},
        name='auth_logout'),

    url(r'^nulstil-kodeord/$',
        auth_views.password_reset,
        {'template_name':'registration/resetPassword.html'},
        name='auth_password_reset'),

    url(r'^nulstil-kodeord/done/$',
        auth_views.password_reset_done,
        {'template_name':'registration/resetPasswordDone.html'},
        name='auth_password_reset_done'),

    url(r'^behandling-af-personoplysninger/$',
        direct_to_template,
        {'template' : 'data-rules.html'},
        name='data_rules'),

    (r'^profil/', include('members.urls')),
    (r'^bliv-medlem/', include('registration.urls')),
    (r'^events/', include('events.urls')),
    (r'^migrate/', include('migration.urls')),
    (r'^accounting/', include('accounting.urls')),
    (r'^booking/', include('booking.urls')),
    (r'^eventmode/', include('eventmode.urls')),
    (r'^mailcenter/', include('mailcenter.urls')),

    # Main site redirection urls
    url(r'^goto/ordensregler/$',
        redirect_to,
        {'url' : 'http://www.anime-kita.dk/regler.html'},
        name = 'goto_eventrules'),

    url(r'goto/vedtaegter/$',
        redirect_to,
        {'url' : 'http://www.anime-kita.dk/vedtaegter.html'},
        name = 'goto_regulations'),

    # Admin urls
    (r'^admin/(.*)', admin.site.root),
)
