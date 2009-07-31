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
            <attribute id="first_name">John Doe</attribute>
            <attribute id="...">...</attribute>
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
        """
        <?xml version="1.0" encoding="utf-8"?>
        <info>
          <user id="%(username)s">
            <attribute id="first_name">%(first_name)s</attribute>
            <attribute id="last_name">%(last_name)s</attribute>
            <attribute id="email">%(email)s</attribute>
          </user>
        </info>
        """ % {'username' : user.username,
               'first_name' : user.first_name,
               'last_name' : user.last_name,
               'email' : user.email}

        return HttpResponse(resp)
