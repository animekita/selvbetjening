import logging

def debug(msg, *args, **kwargs):
    kwargs['extra'] = {'clientip': '', 'user': ''}

    logging.getLogger('').debug(msg, *args, **kwargs)

def info(request, msg, *args, **kwargs): 
    logging.getLogger('').info(u'%s %s' + msg, 
                               request.META.get('REMOTE_ADDR', '?.?.?.?'),
                               request.user.username,
                               *args, **kwargs)