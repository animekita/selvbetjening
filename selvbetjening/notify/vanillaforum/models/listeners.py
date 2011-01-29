from django.core.mail import mail_admins

from selvbetjening.notify import BaseListener

from remote import RemoteUser, RemoteUserAssociation

class UserChangedListener(BaseListener):

    def handler(self, sender, **kwargs):
        user = kwargs['instance']
        created = kwargs['created']

        if created:
            self._insert_user(user)
        else:
            self._update_user(user)

    def _insert_user(self, user):
        remote_user = RemoteUser.objects.using(self._database_id)\
                                        .create(username=user.username,
                                                email=user.email)

        RemoteUserAssociation.objects.using(self._database_id)\
                                     .create(selv_user_id=user.id,
                                             remote_user_id=remote_user.id)

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
            remote_user = RemoteUserAssociation.objects.using(self._database_id)\
                                                       .get(selv_user_id=user.id)

            remote_user.delete()

        except RemoteUserAssociation.DoesNotExist:
            pass
