import os
import sys

path_to_virtualenv_file = '/path/activate_this.py'

execfile(path_to_virtualenv_file, dict(__file__=path_to_virtualenv_file))

os.environ['DJANGO_SETTINGS_MODULE'] = 'path.to.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()