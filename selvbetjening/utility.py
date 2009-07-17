from django.core.exceptions import ImproperlyConfigured

def import_function(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = __import__(module, {}, {}, [attr])
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' % (module, e))
    try:
        func = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a callable function "%s" ' % (module, attr))
    
    return func