DEBUG = True
TEMPLATE_DEBUG = DEBUG
STATIC_DEBUG = DEBUG
CRISPY_FAIL_SILENTLY = not DEBUG

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# session settings
SESSION_COOKIE_NAME = 'kita_auth_token'
SESSION_COOKIE_DOMAIN = '.alpha.kita.dk'

DATABASES = {
    'default': {
        'NAME': 'default',
        'ENGINE': 'django.db.backends.sqlite3',
        },
    'ext_database1': {
        'NAME': 'ext_database1',
        'ENGINE': 'django.db.backends.sqlite3',
        },
    'ext_database2': {
        'NAME': 'ext_database2',
        'ENGINE': 'django.db.backends.sqlite3',
        }
}

# Site url (no trailing slash)
SITE_URL = 'http://localhost:8000'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin media
# USE TRAILING SLASH
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Make this unique, and don't share it with anybody.
# Remember to change this!
SECRET_KEY = 'lic-@(-)mi^b&amp;**h1ggnbyya2qiivaop-@c#3@m3w%m1o73j8@'


# Notify configurations

"""
NOTIFY_CONCRETE5['example'] = {'database_id' : 'DATABASE_ID'}
"""
NOTIFY_CONCRETE5 = []

"""
NOTIFY_PROFTPD['example'] = {'database_id' : 'DATABASE_ID',
                             'default_gid' : 1,
                             'default_uid' : 1,
                             'ftp_dir' : '/var/ftp/',
                             'username_format' : '%s@domain.tld'}
"""
NOTIFY_PROFTPD = []

"""
NOTIFY_VANILLAFORUM['example'] = {'database_id' : 'DATABASE_ID',
                                  'default_role_id' : 'default_ROLE_ID'}
"""
NOTIFY_VANILLAFORUM = []