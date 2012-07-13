from django.dispatch import Signal
from django.contrib.auth.models import User
from django.db.models.signals import pre_save

user_changed_username = Signal(providing_args=['old_username', 'new_username'])
user_changed_password = Signal(providing_args=['instance', 'clear_text_password'])
user_created = Signal(providing_args=['instance', 'clear_text_password'])

# hijack the django set_password function for users
# origin: http://www.djangosnippets.org/snippets/397/
real_set_password = User.set_password

def set_password(self, raw_password):
    if self.id is None:
        self.save()

    real_set_password(self, raw_password)

    # signal changed password
    user_changed_password.send(sender=self, instance=self, clear_text_password=raw_password)

# replace the method
User.set_password = set_password

# listen er changed username
def username_changed_listener(sender, **kwargs):
    new_user = kwargs['instance']

    try:
        old_user = User.objects.get(pk=new_user.pk)

        if new_user.username != old_user.username:
            user_changed_username.send(new_user,
                                       old_username=old_user.username,
                                       new_username=new_user.username)

    except User.DoesNotExist:
        pass # the user was created

pre_save.connect(username_changed_listener, sender=User)