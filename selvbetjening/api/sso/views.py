from django.http import HttpResponse

import models

def validate(request, service, auth_token):
    """
    Returns "rejected" on reject and "accepted/username" on accept
    """
    user = models.get_user_from_token(service, auth_token)

    if user is None:
        return HttpResponse(u'rejected')

    return HttpResponse(u'accepted/%s' % user.username)

def info(request, service, auth_token):
    """
    Returns xml blob on the format.
    <info>
        <user id="username">
            <first_name>John Doe</first_name>
            ...
        </user>
    </info>

    If token is invalid the string "rejected" is returned.
    """

    user = models.get_user_from_token(service, auth_token)

    if user is None:
        return HttpResponse(u'rejected')
    else:
        resp = \
        """<?xml version="1.0" encoding="utf-8"?>
        <info>
          <user id="%(username)s">
            <username>%(username)s</username>
            <first_name>%(first_name)s</first_name>
            <last_name>%(last_name)s</last_name>
            <email>%(email)s</email>
          </user>
        </info>
        """ % {'username' : user.username,
               'first_name' : user.first_name,
               'last_name' : user.last_name,
               'email' : user.email}

        return HttpResponse(resp)
