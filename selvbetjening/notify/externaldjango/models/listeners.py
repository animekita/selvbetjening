from django.contrib.auth.models import Group

from selvbetjening.notify import BaseListener

from native import GroupDjangoGroup
from externaldjango import DjangoGroup, DjangoUser

class GroupMembersChangedListener(BaseListener):
    def handler(self, sender, **kwargs):
        """
        Called if changes has been made to the user<=>group association, adding or
        removing users from the groups on all target installations.
        """

        user = kwargs.get('instance')
        action = kwargs.get('action')
        model = kwargs.get('model')
        group_pks = kwargs.get('pk_set')

        if isinstance(user, DjangoUser):
            # ignore actions done on DjangoUser instances,
            # since these are done on the external sites and thus
            # is of no concern for this handler
            return

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
            djangoGroup = DjangoGroup.objects.get(group=group_pk,
                                              database_id=self._database_id)
        except DjangoGroup.DoesNotExist:
            # group not present in external django, ignore.
            return

        try:
            djangoUser = DjangoUser.objects.\
                                    using(self._database_id).\
                                    get(username=user.username)

        except DjangoUser.DoesNotExist:
            djangoUser = DjangoUser.objects.\
                                    using(self._database_id).\
                                    create(username=user.username)

        djangoUser.groups.add(djangoGroup)

    def _remove_handler(self, user, group_pk):
        try:
            djangoGroup = DjangoGroup.objects.get(group=group_pk,
                                                  database_id=self._database_id)
        except DjangoGroup.DoesNotExist:
            # group not present in concrete5, ignore.
            return

        try:
            djangoUser = DjangoUser.objects.\
                                    using(self._database_id).\
                                    get(username=user.username)

            djangoGroup.user_set.remove(djangoUser)

        except DjangoUser.DoesNotExist:
            pass

    def _clear_handler(self, user):
        try:
            djangoUser = DjangoUser.objects.\
                                    using(self._database_id).\
                                    get(username=user.username)

            djangoUser.groups.clear()

        except DjangoUser.DoesNotExist:
            pass

class UserChangedUsernameListener(BaseListener):
    def handler(self, sender, **kwargs):
        old_username = kwargs['old_username']
        new_username = kwargs['new_username']

        try:
            user = DjangoUser.objects.\
                              using(self._database_id).\
                              get(username=old_username)

            user.username = new_username
            user.save()

        except DjangoUser.DoesNotExist:
            pass
