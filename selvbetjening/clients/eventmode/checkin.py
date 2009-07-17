from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from selvbetjening import utility

_checkin_processors = None

def get_checkin_processors():
    """
    Checkin processors are listed in the EVENTMODE_CHECKIN_PROCESSORS
    variable in django settings. Each item in the list defines the
    path to a checkin processor function.

    The function signature is as follows:
    func(request, user, event) -> (checkin_allowed, render_function)

    The render_function is a function, taking no arguments, which
    returns a part of a web-page to be used in the checkin process.
    """
    global _checkin_processors
    if _checkin_processors is None:
        processors = []
        for path in settings.EVENTMODE_CHECKIN_PROCESSORS:
            func = utility.import_function(path)
            processors.append(func)

        _checkin_processors = tuple(processors)
    return _checkin_processors