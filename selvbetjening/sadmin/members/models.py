from selvbetjening.sadmin.base.sadmin import site

import urls
import nav

site.register_urls('members', urls.url_patterns)
