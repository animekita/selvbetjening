from django.conf.urls.defaults import patterns, url, include
from django.template import RequestContext

import nav

class SAdmin(object):
    def __init__(self):
        self._urls = []

    def register_urls(self, module, url_pattern):
        self._urls.append((module, url_pattern))

    @property
    def urls(self):
        url_patterns = patterns('selvbetjening.sadmin.base.views',
            url(r'^$', 'dashboard', name='dashboard'),
            *[(r'^%s/' % module, include(url_pattern)) for module, url_pattern in self._urls]
        )

        return (url_patterns, 'sadmin', 'sadmin')

site = SAdmin()

class SAdminContext(RequestContext):
    def __init__(self, *args, **kwargs):
        super(SAdminContext, self).__init__(*args, **kwargs)