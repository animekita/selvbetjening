import logging

def debug(msg, *args, **kwargs):
    kwargs['extra'] = {'clientip': '', 'user': ''}

    logging.getLogger('').debug(msg, *args, **kwargs)

def info(request, msg, *args, **kwargs):
    kwargs['extra'] = {'clientip': request.META.get('REMOTE_ADDR', '?.?.?.?'),
                                      'user':request.user.username}
    logging.getLogger('').info(msg, *args, **kwargs)