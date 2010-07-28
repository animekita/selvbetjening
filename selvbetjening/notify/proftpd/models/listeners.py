import hashlib
import base64

from django.contrib.auth.models import Group

from selvbetjening.notify import BaseListener
from selvbetjening.data.members.signals import user_changed_password, user_created

from native import GroupProftpdGroup, CompatiblePassword
from proftpd import ProftpdGroup, ProftpdUser

class GroupMembersChangedListener(BaseListener):
    def __init__(self, listener_id, config):
        self._gid = config['default_gid']
        self._uid = config['default_uid']
        self._ftpdir = config['ftp_dir']

        super(GroupMembersChangedListener, self).__init__(listener_id, config)

    def handler(self, sender, **kwargs):
        """
        Called if changes has been made to the user<=>group association, adding or
        removing users from the groups on all target installations.
        """

        user = kwargs.get('instance')
        action = kwargs.get('action')
        model = kwargs.get('model')
        group_pks = kwargs.get('pk_set')

        if not model is Group:
            # ignore non-group changes.
            return

        if action == 'post_add':
            for group_pk in group_pks:
                self._add_handler(user, group_pk)

        elif action == 'post_remove':
            for group_pk in group_pks:
                self._remove_handler(user, group_pk)

        elif action == 'post_clear':
            self._clear_handler(user)

    def _add_handler(self, user, group_pk):
        try:
            proftpdGroup = ProftpdGroup.objects.get(group=group_pk,
                                                    database_id=self._database_id)

        except ProftpdGroup.DoesNotExist:
            # group not present in proftpd or not associated, ignore.
            pass

        username = self._config['username_format'] % user.username

        try:
            ProftpdUser.objects.using(self._database_id).\
                                get(username=username)

        except ProftpdUser.DoesNotExist:
            try:
                compatiblePassword = CompatiblePassword.objects.get(user=user)
                password = compatiblePassword.password
            except CompatiblePassword.DoesNotExist:
                password = '{none}'

            ProftpdUser.objects.using(self._database_id).\
                                create(username=username,
                                       password=password,
                                       gid=self._gid,
                                       uid=self._uid,
                                       ftpdir=self._ftpdir)

        if not proftpdGroup.is_member(username):
            proftpdGroup.add_member(username)

    def _remove_handler(self, user, group_pk):
        try:
            proftpdGroup = ProftpdGroup.objects.get(group=group_pk,
                                                    database_id=self._database_id)

        except ProftpdGroup.DoesNotExist:
            # group not present in proftpd or not associated, ignore.
            pass

        username = self._config['username_format'] % user.username

        proftpdGroup.remove_member(username)

    def _clear_handler(self, user):
        username = self._config['username_format'] % user.username

        proftpdGroups = ProftpdGroup.objects.using(self._database_id).all()

        for proftpdGroup in proftpdGroups:
            proftpdGroup.remove_member(username)

class MemberPasswordChangedListener(BaseListener):
    def handler(self, sender, **kwargs):
        compatiblePassword = kwargs.get('instance')
        user = compatiblePassword.user

        username = self._config['username_format'] % user.username

        try:
            proftpdUser = ProftpdUser.objects.using(self._database_id).\
                                              get(username=username)

            proftpdUser.password = compatiblePassword.password
            proftpdUser.save()

        except ProftpdUser.DoesNotExist:
            pass

class UserChangedUsernameListener(BaseListener):
    def handler(self, sender, **kwargs):
        old_username = self._config['username_format'] % kwargs['old_username']
        new_username = self._config['username_format'] % kwargs['new_username']

        try:
            proftpdUser = ProftpdUser.objects.using(self._database_id).\
                                              get(username=old_username)

            proftpdUser.username = new_username
            proftpdUser.save()

            for group in ProftpdGroup.objects.using(self._database_id).all():
                if group.is_member(old_username):
                    group.remove_member(old_username)
                    group.add_member(new_username)

        except ProftpdUser.DoesNotExist:
            pass

def user_password_changed_or_set(sender, **kwargs):
    user = kwargs['instance']
    clear_text_password = kwargs['clear_text_password']

    password_hash = hashlib.sha1(clear_text_password).digest()
    password = '{sha1}%s' % base64.b64encode(password_hash)

    try:
        compatiblePassword = CompatiblePassword.objects.get(user=user)
        compatiblePassword.password = password
        compatiblePassword.save()
    except CompatiblePassword.DoesNotExist:
        CompatiblePassword.objects.create(user=user, password=password)

user_created.connect(user_password_changed_or_set)
user_changed_password.connect(user_password_changed_or_set)