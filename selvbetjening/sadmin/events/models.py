from selvbetjening.sadmin.base.sadmin import site

import urls
import nav

site.register_urls('events', urls.url_patterns)
