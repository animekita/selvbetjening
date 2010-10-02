from django.utils.translation import ugettext_lazy as _

from selvbetjening.sadmin.base.sadmin import site

import urls

site.register_urls('members', urls.url_patterns)
site.register_navigation(_('Members'), 'sadmin:members_list') 