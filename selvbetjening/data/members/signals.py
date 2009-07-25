from django.dispatch import Signal

user_changed_password = Signal(providing_args=['instance', 'clear_text_password'])
user_created = Signal(providing_args=['instance', 'clear_text_password'])

# hijack the django set_password function for users
# origin: http://www.djangosnippets.org/snippets/397/
from django.contrib.auth.models import User

real_set_password = User.set_password

def set_password(self, raw_password):
    if self.id == None:
        self.save()

    real_set_password(self, raw_password)

    # signal changed password
    user_changed_password.send(sender=self, instance=self, clear_text_password=raw_password)

# replace the method
User.set_password = set_password
