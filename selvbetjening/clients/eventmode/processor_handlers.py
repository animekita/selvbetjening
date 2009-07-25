from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from selvbetjening import utility

"""
processor(request, attendee)
view()
save()
"""
change_selections = utility.ProcessorHandler(settings, 'EVENTMODE_CHECKIN_PROCESSORS')
