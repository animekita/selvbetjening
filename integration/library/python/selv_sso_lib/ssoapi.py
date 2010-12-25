import re
import urllib2
import urllib
from xml.sax.handler import ContentHandler
from xml.sax import parseString

SERVICE_ID = 'test'
AUTH_TOKEN_KEY = 'kita_auth_token'
SELVBETJENING_API = 'http://alpha.kita.dk:8001'

class AuthenticationServerException(Exception) : pass
class ErrorContactingAuthenticationServerException(AuthenticationServerException) : pass
class AuthenticationServerReturnsErrorException(AuthenticationServerException) : pass
class ErrorParsingResponseException(AuthenticationServerException) : pass

class AuthWrongCredentialsException(Exception) : pass
class AuthUserInactiveException(Exception) : pass
class AuthMalformedInputException(Exception) : pass
class AuthUnknownException(Exception) : pass

class InfoNoAuthenticatedUserException(Exception) : pass

class SelvbetjeningResponseHandler(ContentHandler):
    def __init__(self):
        self.success = False
        self.error_code = None

        self.auth_token = None

        self.session = None
        self.user = None

        self._buffer = u''
        self._session_tags = ('auth_token', 'expire', 'path', 'domain')
        self._user_tags = ('username', 'first_name', 'last_name', 'email', 'date_joined')

    def startElement(self, name, attrs):
        if name == 'user':
            self.user = {}
        elif name == 'session':
            self.session = {}

    def endElement(self, name):
        if name in self._user_tags:
            self.user[name] = self._buffer
        elif name in self._session_tags:
            self.session[name] = self._buffer
        elif name == 'success':
            self.success = self._buffer == u'True'
        elif name == 'error_code':
            self.error_code = self._buffer

        self._buffer = u''

    def characters(self, char):
        self._buffer += char.replace('\n', '').strip()

class SelvbetjeningIntegrationSSO(object):
    def __init__(self, auth_token=None):
        if auth_token is None:
            self._auth_token = None
        else:
            auth_token_regex = re.compile(r'^[a-z0-9]+$')
            if auth_token_regex.match(auth_token) is not None:
                self._auth_token = auth_token
            else:
                self._auth_token = None

    def authenticate(self, username, password):
        url = '%s/authenticate/%s/' % (SELVBETJENING_API, SERVICE_ID)
        response = self._call(url, {'username' : username, 'password' : password})

        authentication = self._parse(response, SelvbetjeningResponseHandler)

        if authentication.success:
            return authentication

        if authentication.error_code == 'auth_wrong_credentials':
            raise AuthWrongCredentialsException
        elif authentication.error_code == 'auth_user_inactive':
            raise AuthUserInactiveException
        elif authentication.error_code == 'auth_malformed_input':
            raise AuthMalformedInputException
        else:
            raise AuthUnknownException

    def is_authenticated(self):
        if self._auth_token is None:
            return False

        url = '%s/validate/%s/%s/' % (SELVBETJENING_API, SERVICE_ID, self._auth_token)
        response = self._call(url)

        if 'accepted' in response:
            return response[len('accepted/'):]

    def get_session_info(self):
        if self._auth_token is None:
            raise InfoNoAuthenticatedUserException

        url = '%s/info/%s/%s/' % (SELVBETJENING_API, SERVICE_ID, self._auth_token)
        response = self._call(url)

        session_info = self._parse(response, SelvbetjeningResponseHandler)

        if not session_info.success:
            raise InfoNoAuthenticatedUserException

        return session_info

    def _call(self, url, post_data=None):
        try:
            if post_data:
                post_data = urllib.urlencode(post_data)
            response = urllib2.urlopen(url, data=post_data)
        except:
            raise ErrorContactingAuthenticationServerException

        return response.read()

    def _parse(self, response, response_handler):
        handler = response_handler()
        parseString(response, handler)
        return handler
