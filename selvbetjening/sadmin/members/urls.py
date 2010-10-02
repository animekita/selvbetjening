from django.conf.urls.defaults import patterns, url

url_patterns = patterns('selvbetjening.sadmin.members.views',
    url(r'^$', 'list', name='members_list'),
    url(r'^view/(?P<username>[a-zA-Z0-9_-]+)/', 'view', name='members_view'),
    url(r'^ajax/search/', 'ajax_search', name='members_ajax_search'),
)