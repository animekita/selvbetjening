from selvbetjening.settings_base import *

ROOT_URLCONF = 'sdemo.urls'

# installed applications
INSTALLED_APPS.extend([

    'selvbetjening.frontend.base',
    'selvbetjening.frontend.auth',
    'selvbetjening.frontend.userportal',
    'selvbetjening.frontend.eventportal',
    'selvbetjening.frontend.eventsingle',

    'sdemo'
])

# Fix, the sdemo fixtures dir is missing from the fixtures list? lets add it manually

import os

FIXTURE_DIRS = (
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures'),
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/auth/log-in/'

# import localsettings, a per deployment configuration file
try:
    from settings_local import *
except ImportError:
    pass
