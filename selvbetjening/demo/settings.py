from selvbetjening.settings_base import *

ROOT_URLCONF = 'demo.urls'

# installed applications
INSTALLED_APPS.extend([
    'selvbetjening.viewbase.forms',
    'selvbetjening.viewbase.googleanalytics',
    'selvbetjening.viewbase.copyright',

    'selvbetjening.portal.quickregistration',
    'selvbetjening.portal.profile',
    'selvbetjening.portal.eventregistration',

    'selvbetjening.notify',
    'selvbetjening.notify.concrete5',
    'selvbetjening.notify.proftpd',
    'selvbetjening.notify.externaldjango',
    'selvbetjening.notify.vanillaforum',

    'selvbetjening.sadmin.base',
    'selvbetjening.sadmin.members',
    'selvbetjening.sadmin.events',
    'selvbetjening.sadmin.mailcenter',

    'selvbetjening.api.rest',

    'selvbetjening.scheckin.legacy',

    ])

# import localsettings, a per deployment configuration file
try:
    from settings_local import *
except ImportError:
    pass