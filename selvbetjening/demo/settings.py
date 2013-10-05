from selvbetjening.settings_base import *

ROOT_URLCONF = 'selvbetjening.demo.urls'

# installed applications
INSTALLED_APPS.extend([
    'selvbetjening.viewbase.forms',
    'selvbetjening.viewbase.googleanalytics',
    'selvbetjening.viewbase.copyright',

    'selvbetjening.portal.quickregistration',
    'selvbetjening.portal.profile',
    'selvbetjening.portal.eventregistration',

    'selvbetjening.sadmin.base',
    'selvbetjening.sadmin.members',
    'selvbetjening.sadmin.events',
    'selvbetjening.sadmin.mailcenter',

    'selvbetjening.demo'
])

# import localsettings, a per deployment configuration file
try:
    from settings_local import *
except ImportError:
    pass
