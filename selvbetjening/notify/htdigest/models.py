import hashlib
import base64

from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings

from selvbetjening.core.members.signals import user_changed_password, user_created

class HTDigestFile(models.Model):
    file_path = models.CharField(max_length=255)
    groups = models.ManyToManyField(Group)

class CompatiblePassword(models.Model):
    user = models.OneToOneField(User, related_name='htdigest_passwd')
    password = models.CharField(max_length=255)

def user_password_changed_or_set(sender, **kwargs):
    user = kwargs['instance']
    clear_text_password = kwargs['clear_text_password']

    if ':' in user.username or ':' in settings.NOTIFY_HTDIGEST_REALM:
        raise ValueError('Illegal escape character in NOTIFY_HTDIGEST_REALM setting or username')

    password = hashlib.md5('%s:%s:%s' % (user.username,
                                         settings.NOTIFY_HTDIGEST_REALM,
                                         clear_text_password)
                           ).hexdigest()

    try:
        compatiblePassword = CompatiblePassword.objects.get(user=user)
        compatiblePassword.password = password
        compatiblePassword.save()
    except CompatiblePassword.DoesNotExist:
        CompatiblePassword.objects.create(user=user, password=password)

user_created.connect(user_password_changed_or_set)
user_changed_password.connect(user_password_changed_or_set)