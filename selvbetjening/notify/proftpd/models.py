import sqlalchemy
import hashlib

from django.db import models
from django.conf import settings
from django.db.models import signals
from django.contrib.auth.models import Group, User

from selvbetjening.data.members.signals import user_changed_password, user_created

import nativemodels
from nativemodels import NativeGroups, NativeUsers

def _wrap_listener(func):
    """
    Helper function creating a database session and closing it after processing
    """

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
    """
    Called if a group is saved, either updating or creating it on the target installation.
    """

    instance = kwargs.get('instance')
    created = kwargs.get('created')

    try:
        group2native = GroupsMapper.objects.get(group=instance, database_id=config['database_id'])
        nativegroup = NativeGroups.get_by_name(session, group2native.native_group_name)

        nativegroup.name = instance.name
        NativeGroups.save(session, nativegroup)

    except GroupsMapper.DoesNotExist:
        nativegroup = NativeGroups(instance.name, config['default_gid'], "")
        NativeGroups.save(session, nativegroup)

        GroupsMapper.objects.create(group=instance,
                                    native_group_name=nativegroup.groupname,
                                    database_id=config['database_id'])

@_wrap_listener
def _get_sync_group_deleted_listener(listener_id, config, session, sender, **kwargs):
    """
    Called if a group is deleted, removing all internal references to the
    group but does NOT delete it on the target installation.
    """

    instance = kwargs.get('instance')

    try:
        group2native = GroupsMapper.objects.get(group=instance, database_id=config['database_id'])

    except GroupsMapper.DoesNotExist:
        pass


@_wrap_listener
def _get_sync_group_members_listener(listener_id, config, session, sender, **kwargs):
    """
    Called if changes has been made to the user<=>group association, adding or
    removing users from the groups on all target installations.
    """

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

                try:
                    compatiblePassword = CompatiblePassword.objects.get(user=instance)
                    password = compatiblePassword.password
                except CompatiblePassword.DoesNotExist:
                    password = '{none}'

                native_user = NativeUsers.get_by_username(session, config['username_format'] % instance.username)

                if native_user is None:
                    native_user = NativeUsers(config['username_format'] % instance.username,
                                              password,
                                              config['default_uid'],
                                              config['default_gid'],
                                              config['ftp_dir'])
                    NativeUsers.save(session, native_user)

                native_group = NativeGroups.get_by_name(session, map.native_group_name)

                if native_group is not None and (config['username_format'] % native_user.username) not in native_group.members:
                    native_group.members = '%s,%s' % (config['username_format'] % native_user.username, native_group.members)
                    NativeGroups.save(session, native_group)



            except GroupsMapper.DoesNotExist:
                # group not present in concrete5, ignore.
                pass

    elif action == 'remove':
        for group in objects:
            try:
                map = GroupsMapper.objects.get(group=group, database_id=config['database_id'])

                native_user = NativeUsers.get_by_username(session, config['username_format'] % instance.username)

                NativeUsers.delete(session, native_user)

            except GroupsMapper.DoesNotExist:
                # group not present in concrete5, ignore.
                pass

    elif action == 'clear':
        native_user = NativeUsers.get_by_username(session, config['username_format'] % instance.username)

        if native_user is not None:
            NativeUsers.delete(session, native_user)



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

for listener_id in getattr(settings, 'NOTIFY_PROFTPD', ()):
    config = settings.NOTIFY_PROFTPD[listener_id]
    connect_listeners(listener_id, config)

class GroupsMapper(models.Model):
    group = models.ForeignKey(Group, related_name='proftpdgroup_set')
    native_group_name = models.CharField(max_length=255)
    database_id = models.CharField(max_length=32)

    class Meta:
        unique_together = ('native_group_name', 'database_id')

class CompatiblePassword(models.Model):
    user = models.OneToOneField(User)
    password = models.CharField(max_length=255)

def user_password_changed_or_set(sender, **kwargs):
    instance = kwargs['instance']
    clear_text_password = kwargs['clear_text_password']

    password = '{sha1}%s' % hashlib.sha1(clear_text_password).hexdigest()

    try:
        compatiblePassword = CompatiblePassword.objects.get(user=instance)
        compatiblePassword.password = password
        compatiblePassword.save()
    except CompatiblePassword.DoesNotExist:
        CompatiblePassword.objects.create(user=instance, password=password)

user_created.connect(user_password_changed_or_set)
user_changed_password.connect(user_password_changed_or_set)