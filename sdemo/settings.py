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

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/auth/log-in/'

# import localsettings, a per deployment configuration file
try:
    from settings_local import *
except ImportError:
    pass
