from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def googleanalytics(account_id):
    script = """
%(starttag)s
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%%3E%%3C/script%%3E"));
%(endtag)s
%(starttag)s
var pageTracker = _gat._getTracker("%(account_id)s");
pageTracker._initData();
pageTracker._trackPageview();
%(endtag)s
"""

    if not settings.DEBUG:
        return script % {'starttag' : '<script type="text/javascript">',
                         'endtag' : '</script>',
                         'account_id' : account_id}
    else:
        return script % {'starttag' : '<!-- DEBUG',
                         'endtag' : '-->',
                         'account_id' : account_id}