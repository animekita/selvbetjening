import logging

def info(request, msg, *args, **kwargs):
    kwargs['extra'] = {'clientip': request.META.get('REMOTE_ADDR', '?.?.?.?'), 
                                      'user':request.user.username}
    logging.getLogger('').info(msg, *args, **kwargs)