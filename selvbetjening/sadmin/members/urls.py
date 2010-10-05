from django.conf.urls.defaults import patterns, url

url_patterns = patterns('selvbetjening.sadmin.members.views',
    url(r'^$', 'list', name='members_list'),

    url(r'^view/access/(?P<username>[a-zA-Z0-9_-]+)/', 'view_access', name='members_view_access'),
    url(r'^view/(?P<username>[a-zA-Z0-9_-]+)/', 'view', name='members_view'),

    url(r'^create/', 'create', name='members_create'),

    url(r'^ajax/search/', 'ajax_search', name='members_ajax_search'),
)