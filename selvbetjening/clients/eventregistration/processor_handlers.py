from django.conf import settings

from selvbetjening import utility

"""
processor(request, user, event)
render_function()
save_function(attendee)
"""
signup = utility.ProcessorHandler(settings, 'EVENTREGISTRATION_SIGNUP_PROCESSORS')

"""
processor(request, user, event)
render_function()
save_function()
"""
change = utility.ProcessorHandler(settings, 'EVENTREGISTRATION_CHANGE_PROCESSORS')