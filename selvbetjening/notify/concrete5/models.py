import sqlalchemy

from django.db import models
from django.conf import settings
from django.db.models import signals
from django.contrib.auth.models import Group, User

from nativemodels import NativeGroups, NativeUsers, NativeUserGroups, usingNativeDatabase

class Listeners(object):
    @classmethod
    def connect(cls):
        listeners = [(signals.post_save, cls._sync_group_changed, Group),
                     (signals.pre_delete, cls._sync_group_deleted, Group),
                     (signals.m2m_changed, cls._sync_group_members, User)]

        for signal, listener, sender in listeners:
            signal.connect(listener, sender=sender)

    @staticmethod
    @usingNativeDatabase
    def _sync_group_changed(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')

        try:
            group2native = GroupsMapper.objects.get(group=instance)
            nativegroup = NativeGroups.get(group2native.native_group_id)

            nativegroup.name = instance.name
            nativegroup.save()

        except GroupsMapper.DoesNotExist:
            group = NativeGroups(instance.name, u'')
            group.save()

            GroupsMapper.objects.create(group=instance, native_group_id=group.id)

    @staticmethod
    @usingNativeDatabase
    def _sync_group_deleted(sender, **kwargs):
        instance = kwargs.get('instance')

        try:
            group2native = GroupsMapper.objects.get(group=instance)
            nativegroup = NativeGroups.get(group2native.native_group_id)

            nativegroup.delete()

        except GroupsMapper.DoesNotExist:
            pass

    @staticmethod
    def _sync_group_members(sender, **kwargs):
        import wingdbstub
        instance = kwargs.get('instance')
        action = kwargs.get('action')
        model = kwargs.get('model')
        field_name = kwargs.get('field_name')
        objects = kwargs.get('objects')

        if not model is Group:
            # ignore non-group changes.
            return

        if action == 'add':
            for group in objects:
                try:
                    map = GroupsMapper.objects.get(group=group)

                    native_user = NativeUsers.get_by_username(instance.username)

                    if native_user is None:
                        native_user = NativeUsers(instance.username, instance.email, instance.date_joined)
                        native_user.save()

                    native_map = NativeUserGroups(native_user.id, map.native_group_id)
                    native_map.save()

                except GroupsMapper.DoesNotExist:
                    # group not present in concrete5, ignore.
                    pass

        elif action == 'remove':
            for group in objects:
                try:
                    map = GroupsMapper.objects.get(group=group)

                    native_user = NativeUsers.get_by_username(instance.username)

                    if native_user is not None:
                        native_map = NativeUserGroups.get(native_user.id, map.native_group_id)
                        native_map.delete()

                except GroupsMapper.DoesNotExist:
                    # group not present in concrete5, ignore.
                    pass

        elif action == 'clear':
            native_user = NativeUsers.get_by_username(instance.username)

            if native_user is not None:
                NativeUserGroups.remove_user(native_user.id)

Listeners.connect()

class GroupsMapper(models.Model):
    group = models.ForeignKey(Group)
    native_group_id = models.PositiveIntegerField(unique=True)



