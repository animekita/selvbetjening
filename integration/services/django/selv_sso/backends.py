from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core import mail

from selv_sso_lib import ssoapi

try:
    ssoapi.SERVICE_ID = settings.SAPI_SERVICE_ID
    ssoapi.AUTH_TOKEN_KEY = settings.SAPI_AUTH_TOKEN_KEY
    ssoapi.SELVBETJENING_API = settings.SAPI_URL

except KeyError:
    raise ImproperlyConfigured('selvbetjening-sso requires the variables SAPI_SERVICE_ID, SAPI_AUTH_TOKEN_KEY, and SAPI_URL to be defined in the settings file.')

class SelvbetjeningBackend(object):

    supports_object_permissions = False
    supports_anonymous_user = True

    def authenticate(self, auth_token=None):
        if auth_token is None:
            return None

        sso = ssoapi.SelvbetjeningIntegrationSSO(auth_token)

        try:
            is_authenticated = sso.is_authenticated()

        except (ssoapi.AuthenticationServerException, ssoapi.AuthUnknownException):
            import sys, traceback

            excinfo = sys.exc_info()
            cls, err = excinfo[:2]

            subject = 'SSO API Error: %s: %s' % (cls.__name__, err)
            message = ''.join(traceback.format_exception(*excinfo))

            mail.mail_admins(subject, message, fail_silently=True)
            return None

        if is_authenticated:
            user, created = User.objects.get_or_create(username=is_authenticated)
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None