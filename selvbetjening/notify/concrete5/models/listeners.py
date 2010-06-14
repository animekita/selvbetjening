from django.contrib.auth.models import Group

from selvbetjening.notify import BaseListener

from native import GroupC5Group
from concrete5 import C5Group, C5User, C5UserGroups

class GroupChangedListener(BaseListener):
    def handler(self, sender, **kwargs):
        """
        Called if a group is changed resulting in two outcomes:
         - The C5 group is updated
         - If no C5 group exists a new group is created
        """

        instance = kwargs.get('instance')
        created = kwargs.get('created')

        try:
            gmap = GroupC5Group.objects.get(group=instance,
                                            database_id=self._database_id)

            c5group = C5Group.objects.\
                    using(self._database_id).\
                    get(pk=gmap.c5group_id)

            c5group.name = instance.name
            c5group.save()

        except GroupC5Group.DoesNotExist:
            c5group = C5Group.objects.\
                    using(self._database_id).\
                    create(name=instance.name, description=u'')

            GroupC5Group.objects.create(group=instance,
                                        c5group_id=c5group.pk,
                                        database_id=self._database_id)

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
            c5group = C5Group.objects.get(group=group_pk,
                                          database_id=self._database_id)
        except C5Group.DoesNotExist:
            # group not present in concrete5, ignore.
            return

        try:
            c5user = C5User.objects.\
                     using(self._database_id).\
                     get(username=user.username)

        except C5User.DoesNotExist:
            c5user = C5User.objects.\
                     using(self._database_id).\
                     create(username=user.username,
                            email=user.email,
                            date_added=user.date_joined)

        C5UserGroups.objects.\
                     using(self._database_id).\
                     create(c5user=c5user, c5group=c5group)

    def _remove_handler(self, user, group_pk):
        try:
            c5group = C5Group.objects.get(group=group_pk,
                                          database_id=self._database_id)
        except C5Group.DoesNotExist:
            # group not present in concrete5, ignore.
            return

        try:
            c5user = C5User.objects.\
                            using(self._database_id).\
                            get(username=user.username)

            C5UserGroups.objects.\
                         using(self._database_id).\
                         get(c5user=c5user, c5group=c5group).delete()

        except C5User.DoesNotExist:
            pass
        except C5UserGroups.DoesNotExist:
            pass

    def _clear_handler(self, user):
        try:
            c5user = C5User.objects.\
                            using(self._database_id).\
                            get(username=user.username)

            C5UserGroups.objects.\
                         using(self._database_id).\
                         filter(c5user=c5user).\
                         delete()

        except C5User.DoesNotExist:
            pass