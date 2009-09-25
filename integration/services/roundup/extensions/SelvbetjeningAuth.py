import os,sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'kita_website.settings'
sys.path.insert(0, '/home/vukitadk/src/selvbetjening.anime-kita.dk/')

execfile('/home/vukitadk/.virtualenvs/selvbetjening/bin/activate_this.py', dict(__file__='/home/vukitadk/.virtualenvs/selvbetjening/bin/activate_this.py'))

from roundup.cgi.actions import LoginAction
from roundup.i18n import _

from django.contrib.auth.models import User

class SelvbetjeningLoginAction(LoginAction):
    def _verify_local_password(self, password):        
        ''' Verify the password that the user has supplied '''
        stored = self.db.user.get(self.client.userid, 'password')
        
        if password == stored:
            return True
        if not password and not stored:
            return True
        
        return False

    def _local_login (self, password):
        ''' Local authentication '''
        
        # make sure the user exists
        try:
            self.client.userid = self.db.user.lookup(self.client.user)
        except KeyError:
            self.client.error_message.append(_('Unknown user "%s"')%self.client.user)
            return False
        
        # verify the password
        if not self._verify_local_password(password):
            self.client.error_message.append(_('Invalid password'))
            return False
        return True

    def _selvbetjening_login(self, password):
        user_authenticated = False
        try:
            selv_user = User.objects.get(username=self.client.user)
            if selv_user.check_password(password):
                user_authenticated = True
        except User.DoesNotExist:
            pass # user does not exist
        
        return user_authenticated

    def _create_profile(self):
        self.journaltag = 'admin'
        
        self.db.user.create(roles=self.db.config.NEW_WEB_USER_ROLES,)
        self.db.commit ()
        
        self.client.userid = self.db.user.lookup(self.client.user)
    
    
    def verifyLogin(self, username, password):

        if self._local_login(password):
            return
            
        if self._selvbetjening_login(password):
            self.client.error_message = []
            return

        self.client.error_message.append(_('Invalid username or password'))        
        self.client.make_user_anonymous()

def init(instance):
    instance.registerAction('login', SelvbetjeningLoginAction)