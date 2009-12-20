import sqlalchemy

from django.db import models
from django.conf import settings
from django.db.models import signals
from django.contrib.auth.models import Group, User

import nativemodels
from nativemodels import NativeGroups, NativeUsers, NativeUserGroups

def _wrap_listener(func):
    def get_listener(listener_id, listener_config):
        def listener(sender, **kwargs):
            session = nativemodels.get_session(listener_config['database_id'])
            result = func(listener_id, listener_config, session, sender, **kwargs)
            session.close()

            return result
        return listener

    return get_listener

@_wrap_listener
def _get_sync_group_changed_listener(listener_id, config, session, sender, **kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created')

    try:
        group2native = GroupsMapper.objects.get(group=instance, database_id=config['database_id'])
        nativegroup = NativeGroups.get(session, group2native.native_group_id)

        nativegroup.name = instance.name
        NativeGroups.save(session, nativegroup)

    except GroupsMapper.DoesNotExist:
        nativegroup = NativeGroups(instance.name, u'')
        NativeGroups.save(session, nativegroup)

        GroupsMapper.objects.create(group=instance,
                                    native_group_id=nativegroup.id,
                                    database_id=config['database_id'])

@_wrap_listener
def _get_sync_group_deleted_listener(listener_id, config, session, sender, **kwargs):
    instance = kwargs.get('instance')

    try:
        group2native = GroupsMapper.objects.get(group=instance, database_id=config['database_id'])
        nativegroup = NativeGroups.get(session, group2native.native_group_id)

        NativeGroups.delete(session, nativegroup)

    except GroupsMapper.DoesNotExist:
        pass

@_wrap_listener
def _get_sync_group_members_listener(listener_id, config, session, sender, **kwargs):
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
                map = GroupsMapper.objects.get(group=group, database_id=config['database_id'])

                native_user = NativeUsers.get_by_username(session, instance.username)

                if native_user is None:
                    native_user = NativeUsers(instance.username, instance.email, instance.date_joined)
                    NativeUsers.save(session, native_user)

                native_map = NativeUserGroups(native_user.id, map.native_group_id)
                NativeUserGroups.save(session, native_map)

            except GroupsMapper.DoesNotExist:
                # group not present in concrete5, ignore.
                pass

    elif action == 'remove':
        for group in objects:
            try:
                map = GroupsMapper.objects.get(group=group, database_id=config['database_id'])

                native_user = NativeUsers.get_by_username(session, instance.username)

                if native_user is not None:
                    native_map = NativeUserGroups.get(session, native_user.id, map.native_group_id)
                    NativeUserGroups.delete(native_map)

            except GroupsMapper.DoesNotExist:
                # group not present in concrete5, ignore.
                pass

    elif action == 'clear':
        native_user = NativeUsers.get_by_username(session, instance.username)

        if native_user is not None:
            NativeUserGroups.remove_user(session, native_user.id)

listeners = {}
def connect_listeners(listener_id, config):
    global listeners

    connections = [(signals.post_save, _get_sync_group_changed_listener, Group),
                   (signals.pre_delete, _get_sync_group_deleted_listener, Group),
                   (signals.m2m_changed, _get_sync_group_members_listener, User)]

    for signal, get_listener_func, sender in connections:
        if listeners.get(listener_id, None) is None:
            listeners[listener_id] = []

        listener = get_listener_func(listener_id, config)
        listeners[listener_id].append(listener)

        signal.connect(listener, sender=sender)

def disconnect_listeners(target_listener_id):
    global listeners
    del listeners[target_listener_id]

for listener_id in getattr(settings, 'NOTIFY_CONCRETE5', ()):
    config = settings.NOTIFY_CONCRETE5[listener_id]
    connect_listeners(listener_id, config)

class GroupsMapper(models.Model):
    group = models.ForeignKey(Group)
    native_group_id = models.PositiveIntegerField()
    database_id = models.CharField(max_length=32)

    class Meta:
        unique_together = ('native_group_id', 'database_id')
