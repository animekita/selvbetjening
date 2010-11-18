from django.conf.urls.defaults import patterns, url, include

url_patterns = patterns('selvbetjening.sadmin.base.views',
    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
)