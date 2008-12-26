from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

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
            i = path.rfind('.')
            module, attr = path[:i], path[i+1:]
            try:
                mod = __import__(module, {}, {}, [attr])
            except ImportError, e:
                raise ImproperlyConfigured('Error importing eventmode checkin processor module %s: "%s"' % (module, e))
            try:
                func = getattr(mod, attr)
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a "%s" callable checkin processor' % (module, attr))
            processors.append(func)

        _checkin_processors = tuple(processors)
    return _checkin_processors