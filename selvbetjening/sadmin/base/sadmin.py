from django.conf.urls.defaults import patterns, url, include
from django.template import RequestContext
from django.core.urlresolvers import reverse

class SAdmin(object):
    def __init__(self):
        self._urls = []
        self._navigation = []
    
    def register_urls(self, module, url_pattern):
        self._urls.append((module, url_pattern))
        
    def register_navigation(self, name, url):
        self._navigation.append({'name': name, 'url': reverse(url)})
    
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
        navigation = {'sadmin_navigation': site._navigation}
        
        if len(args) > 1:
            args[1].extend(navigation)
        else:
            args = (args[0], navigation)
            
        super(SAdminContext, self).__init__(*args, **kwargs)