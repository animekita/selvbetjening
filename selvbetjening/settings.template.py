# template for per instance settings file
from selvbetjening.settings_base import *

import os
DIRNAME = os.path.abspath(os.path.dirname(__file__))

# email
DEFAULT_FROM_EMAIL = 'noreply@anime-kita.dk'
SERVER_EMAIL = 'noreply@anime-kita.dk'

# various settings
ROOT_URLCONF = 'selvbetjening.urls'

ADMINS = (
    #('admin', 'admin@example.org'),
)

# template directories
TEMPLATE_DIRS = [
    os.path.join(DIRNAME, 'templates')
].extend(TEMPLATE_DIRS)

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

    'selvbetjening.api.sso',
])

# processors
# Insert required processors

# import localsettings, a per deployment configuration file
try:
    from settings_local import *
except ImportError:
    pass
