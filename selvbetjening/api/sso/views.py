import time

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate as auth_authenticate
from django.shortcuts import render_to_response
from django.template import RequestContext

import models
import forms

class ErrorCodes(object):
    INFO_USER_NOT_AUTHENTICATED = 'info_user_not_authenticated'

    AUTH_WRONG_CREDENTIALS = 'auth_wrong_credentials'
    AUTH_USER_INACTIVE = 'auth_user_inactive'
    AUTH_MALFORMED_INPUT = 'auth_malformed_input'

def validate(request, service, auth_token):
    """
    Returns "rejected" on reject and "accepted/username" on accept
    """
    user = models.get_user_from_token(auth_token)

    if user is None:
        return HttpResponse(u'rejected')

    return HttpResponse(u'accepted/%s' % user.username)

def authenticate(request, service,
                 template_name='api/sso/base.xml'):
    """
    Returns xml blob in the following format. Only accepts POST requests.

    <result>
      <success>True|False</success>
      <error_code>ERROR_CODE</error_code>
      <session>
        ...
      </session>
      <user>
        ...
      </user>
    </result>

    """

    if request.method != 'POST':
        return HttpResponseBadRequest()

    form = forms.AuthenticateInputForm(request.POST)

    data = {}

    if not form.is_valid():
        return render_to_response(template_name, {'success' : False,
                                                  'error_code' : ErrorCodes.AUTH_MALFORMED_INPUT})

    username = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password')

    user = auth_authenticate(username=username, password=password)

    if user is None:
        return render_to_response(template_name, {'success' : False,
                                                  'error_code' : ErrorCodes.AUTH_WRONG_CREDENTIALS})

    if not user.is_active:
        return render_to_response(template_name, {'success' : False,
                                                  'error_code' : ErrorCodes.AUTH_USER_INACTIVE})

    session = models.get_new_user_session(user)

    session_data = {'auth_token' : session.session_key,
                    'expire' : time.mktime(session.get_expiry_date().timetuple()),
                    'path' : settings.SESSION_COOKIE_PATH,
                    'domain': settings.SESSION_COOKIE_DOMAIN}

    return render_to_response(template_name,
                              {'success' : True,
                               'user' : user,
                               'session' : session_data,
                               'groups' : _filter_groups(user, service)})

def info(request, service, auth_token,
         template_name='api/sso/base.xml'):
    """
    Returns xml blob on the format.
    <result>
      <success>True|False</success>
      <error_code>ERROR_CODE</error_code>

      <user id="username">
        ...
      </user>
    </result>

    """

    user = models.get_user_from_token(auth_token)

    data = {}

    if user is None:
        data['success'] = False
        data['error_code'] = ErrorCodes.INFO_USER_NOT_AUTHENTICATED
    else:
        data['success'] = True
        data['user'] = user
        data['groups'] = _filter_groups(user, service)

    return render_to_response(template_name, data)

def _filter_groups(user, service):
    try:
        service = models.Service.objects.get(pk=service)
        groups = user.groups.filter(service=service)
    except models.Service.DoesNotExist:
        groups = user.groups.all()

    return groups
