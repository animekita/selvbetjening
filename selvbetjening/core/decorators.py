import logger

def log_access(view_func):
    def view_access_logger(request, *args, **kwargs):
        logger.info(request,
                    'client visited view: %s.%s' % (view_func.__module__, view_func.__name__))
        return view_func(request, *args, **kwargs)

    return view_access_logger