import re
import urllib2
from xml.sax.handler import ContentHandler
from xml.sax import parseString

class AuthenticationServerException(Exception) : pass
class ErrorContactingAuthenticationServerException(AuthenticationServerException) : pass
class AuthenticationServerReturnsErrorException(AuthenticationServerException) : pass
class ErrorParsingResponseException(AuthenticationServerException) : pass

class AuthWrongCredentialsException(Exception) : pass
class AuthUserInactiveException(Exception) : pass
class AuthMalformedInputException(Exception) : pass
class AuthUnknownException(Exception) : pass

class InfoNoAuthenticatedUserException(Exception) : pass

class SelvbetjeningAuthenticationHandler(ContentHandler):
    pass

class SelvbetjeningSessionInfoHandler(ContentHandler):
    def __init__(self):
        self.success = False
        self.error_code = None

        self.auth_token = None

        self.session = None
        self.user = None

        self._buffer = u''
        self._user_tags = ('username', 'first_name', 'last_name', 'email', 'date_joined')

    def startElement(self, name, attrs):
        if name == 'user':
            self.user = {}

    def endElement(self, name):
        if name in self._user_tags:
            self.user[name] = self._buffer
        elif name == 'success':
            self.success = self._buffer == u'True'
        elif name == 'error_code':
            self.error_code = self._buffer

        self._buffer = u''

    def characters(self, char):
        self._buffer += char.replace('\n', '').strip()

class SelvbetjeningIntegrationSSO(object):
    SERVICE_ID = 'test'
    AUTH_TOKEN_KEY = 'kita_auth_token'
    SELVBETJENING_API = 'http://test.selvbetjening.dk:8001'

    def __init__(self, cookies):
        self.cookies = cookies
        token = cookies.get(self.AUTH_TOKEN_KEY, None)

        if token is None:
            self._auth_token = None
        else:
            auth_token_regex = re.compile(r'^[a-z0-9]+$')
            if auth_token_regex.match(token) is not None:
                self._auth_token = token
            else:
                self._auth_token = None

    def authenticate(self, username, password):
        # not implemented

        #url = '%s/authenticate/%s/' % (self.SELVBETJENING_API, self.SERVICE_ID)
        #response = self._call(url, {'username' : username, 'password' : password})

        #authentication = self._parse(response, SelvbetjeningAuthenticationHandler)

        #if authentication.success:
        #    self.cookies.set(self.AUTH_TOKEN_KEY, authentication.auth_token)

        pass

    def is_authenticated(self):
        if self._auth_token is None:
            return False

        url = '%s/validate/%s/%s/' % (self.SELVBETJENING_API, self.SERVICE_ID, self._auth_token)
        response = self._call(url)

        if 'accepted' in response:
            return response[len('accepted/'):]

    def get_session_info(self):
        if self._auth_token is None:
            raise InfoNoAuthenticatedUserException

        url = '%s/info/%s/%s/' % (self.SELVBETJENING_API, self.SERVICE_ID, self._auth_token)
        response = self._call(url)

        session_info = self._parse(response, SelvbetjeningSessionInfoHandler)

        if not session_info.success:
            raise InfoNoAuthenticatedUserException

        return session_info

    def _call(self, url, post_data=None):
        try:
            response = urllib2.urlopen(url, post_data)
        except  urllib2.HTTPError as exception:
            raise ErrorContactingAuthenticationServerException(exception)

        return response.read()

    def _parse(self, response, response_handler):
        handler = response_handler()
        #saxparser = make_parser()
        #saxparser.setContentHandler(handler)
        #saxparser.parse(response)
        parseString(response, handler)
        return handler

