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

class ProcessorHandler(object):
    def __init__(self, processor_list):
        self._processors = None
        self._processor_list = processor_list

    def get_processors(self):
        if self._processors is None:
            processors = []
            for path in self._processor_list:
                func = import_function(path)
                processors.append(func)

            self._processors = tuple(processors)
        return self._processors

    def run_processors(self, *args, **kwargs):
        submit_allowed_by_all = True
        render_functions = []
        save_functions = []

        for processor in self.get_processors():
            submit_allowed, render_func, save_func = processor(*args, **kwargs)

            if not submit_allowed:
                submit_allowed_by_all = False

            render_functions.append(render_func)
            save_functions.append(save_func)

        return (submit_allowed_by_all, render_functions, save_functions)