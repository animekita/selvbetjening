import hashlib
import random
import phpserialize

from django.core.mail import mail_admins
from django.conf import settings

from selvbetjening.notify import BaseListener

from remote import RemoteUser, RemoteUserRole, RemoteUserAssociation
from native import Settings

def register_new_user(database_id, default_role_id, user):
    random_pass = hashlib.sha1(str(random.randint(0, 99999999))).hexdigest()

    remote_user = RemoteUser.objects.using(database_id)\
                                    .create(username=user.username,
                                            password=random_pass,
                                            email=user.email)

    RemoteUserRole.objects.using(database_id)\
                          .create(user_id=remote_user.id,
                                  role_id=default_role_id)

    RemoteUserAssociation.objects.using(database_id)\
                                 .create(selv_user_id=user.id,
                                         remote_user_id=remote_user.id)

    user_settings, created = Settings.objects.get_or_create(user=user)

    update_user_settings(database_id, user_settings)

def update_user_settings(database_id, user_settings):
    rel = RemoteUserAssociation.objects.using(database_id)\
                                           .get(selv_user_id=user_settings.user.pk)

    remote_user = RemoteUser.objects.using(database_id)\
                                    .get(id=rel.remote_user_id)

    if remote_user.preferences:
        preferences = phpserialize.loads(remote_user.preferences)
    else:
        preferences = {}

    user_settings.update_preferences(preferences)

    remote_user.preferences = phpserialize.dumps(preferences)
    remote_user.photo_url = '%s%s' % (settings.MEDIA_URL, user_settings.picture)

    remote_user.save()

class UserChangedListener(BaseListener):

    def handler(self, sender, **kwargs):
        user = kwargs['instance']
        created = kwargs['created']

        if created:
            register_new_user(self._database_id, self._config['default_role_id'], user)
        else:
            self._update_user(user)

    def _update_user(self, user):
        try:
            association = RemoteUserAssociation.objects.using(self._database_id)\
                                                       .get(selv_user_id=user.pk)
            remote_user = RemoteUser.objects.using(self._database_id)\
                                            .get(id=association.remote_user_id)

            remote_user.username = user.username
            remote_user.email = user.email
            remote_user.save()

        except RemoteUserAssociation.DoesNotExist:
            mail_admins(u'Please sync Selvbetjening with your Vanilla Forum installation',
                        u'The user named %s has just been changed, but a matching user in your vanilla forum installation could not be found. This indicates that these are out of sync. Please use the management commands to sync Selvbetjening with Vanilla.' % user.username)

class UserDeletedListener(BaseListener):

    def handler(self, sender, **kwargs):
        user = kwargs['instance']

        try:
            RemoteUserAssociation.objects.using(self._database_id)\
                                         .get(selv_user_id=user.id)\
                                         .delete()

        except RemoteUserAssociation.DoesNotExist:
            pass

class SettingsChangedListener(BaseListener):

    def handler(self, sender, **kwargs):
        user_settings = kwargs['instance']
        created = kwargs['created']

        if not created:
            update_user_settings(self._database_id, user_settings)


# change notification settings
# change user groups