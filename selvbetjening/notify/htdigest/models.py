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

def filter_username(username):
    """
    Usernames starting with @ are incompatible with the authz file format which
    is used with the htdigest files for access control. Replace the @ with an !
    which is normally not allowed for usernames, thus avoiding naming clashes.
    """

    if username[0] == '@':
        return username.replace('@', '!', 1)
    else:
        return username

def user_password_changed_or_set(sender, **kwargs):
    user = kwargs['instance']
    clear_text_password = kwargs['clear_text_password']

    password = hashlib.md5('%s:%s:%s' % (filter_username(user.username),
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