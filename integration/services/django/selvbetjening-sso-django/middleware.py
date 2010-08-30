from django.contrib import auth
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from datetime import datetime, timedelta

class SelvbetjeningUserMiddleware(object):
    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")

        try:
            auth_token = request.COOKIES[settings.SAPI_AUTH_TOKEN_KEY]

        except KeyError:
            # token not set, user is thus not logged in

            if request.user.is_authenticated():
                auth.logout(request)

            return

        if request.user.is_authenticated() and \
           request.session.get('auth_token', '') == auth_token and \
           request.session.get('auth_token_timeout', datetime.now()) > datetime.now():
            # user is logged in with current auth token
            return

        user = auth.authenticate(auth_token=auth_token)

        if user is None:
            # token invalid, ignore

            if request.user.is_authenticated():
                auth.logout(request)

            return

        if request.user.is_authenticated() and \
           request.user.username == user.username:
            # is already logged in
            pass
        else:
            request.user = user
            auth.login(request, user)

        request.session['auth_token'] = auth_token
        request.session['auth_token_timeout'] = datetime.now() + timedelta(seconds=60)