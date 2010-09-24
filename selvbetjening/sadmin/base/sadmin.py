from django.conf.urls.defaults import patterns, url

class SAdmin(object):
    @property
    def urls(self):
        url_patterns = patterns('selvbetjening.sadmin.base.views',
            url(r'^$', 'dashboard', name='dashboard'),
        )

        return (url_patterns, 'sadmin', 'sadmin')

site = SAdmin()