from roundup.cgi.actions import LoginAction
from roundup.cgi import exceptions
from roundup.i18n import _

import ssoapi

class SelvbetjeningLoginAction(LoginAction):
    def verifyLogin(self, username, password):
        sso = ssoapi.SelvbetjeningIntegrationSSO()

        try:
            sso.authenticate(username, password)
        except ssoapi.AuthWrongCredentialsException:
            raise exceptions.LoginError, self._('Invalid login')
        except ssoapi.AuthUserInactiveException:
            raise exceptions.LoginError, self._('Inactive user')
        except ssoapi.AuthMalformedInputException:
            raise exceptions.LoginError, self._('Malformed credentials')
        except ssoapi.AuthUnknownException:
            raise exceptions.LoginError, self._('Unknown authentication error')
        except ssoapi.AuthenticationServerException:
            raise exceptions.LoginError, self._('Authentication server error')

        try:
            self.db.user.lookup(username)
        except KeyError:
            self._create_profile(username)

    def _create_profile(self, username):
        self.journaltag = 'admin'

        self.db.user.create(username=username, roles=self.db.config.NEW_WEB_USER_ROLES)
        self.db.commit()

def init(instance):
    instance.registerAction('login', SelvbetjeningLoginAction)