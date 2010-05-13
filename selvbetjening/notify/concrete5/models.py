from django.db import models
from django.conf import settings
from django.db.models import signals
from django.contrib.auth.models import Group, User

from selvbetjening.core.database.dbrouter import DatabaseRouter

class GroupC5Group(models.Model):
    group = models.ForeignKey(Group)
    c5group_id = models.PositiveIntegerField(db_column='c5group_id')
    database_id = models.CharField(max_length=32)

    objects = models.Manager()

    class Meta:
        db_table = 'GroupC5Group'
        unique_together = ('c5group_id', 'database_id')

class C5Group(models.Model):
    id = models.AutoField(primary_key=True, unique=True, db_column='gID')
    name = models.CharField(max_length=128, db_column='gName')
    description = models.CharField(max_length=255, db_column='gDescription')

    objects = models.Manager()

    class Meta:
        db_table = 'Groups'
        managed = False

class C5User(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, db_column='uID')
    username = models.CharField(max_length=64, db_column='uName')
    email = models.CharField(max_length=64, db_column='uEmail')
    password = models.CharField(max_length=255, db_column='uPassword')

    is_active = models.BooleanField(db_column='uIsActive', blank=True, default=1)
    is_validated = models.BooleanField(db_column='uIsValidated', blank=True, default=-1)
    is_full_record = models.BooleanField(db_column='uIsFullRecord', blank=True, default=1)

    date_added = models.DateTimeField(db_column='uDateAdded')

    last_online = models.IntegerField(db_column='uLastOnline', blank=True, default=0)
    last_login = models.IntegerField(db_column='uLastLogin', blank=True, default=0)
    previous_login = models.IntegerField(db_column='uPreviousLogin', blank=True, default=0)
    num_logins = models.IntegerField(db_column='uNumLogins', blank=True, default=0)

    timezone = models.CharField(max_length=255, db_column='uTimezone', blank=True, null=True)
    has_avatar = models.BooleanField(db_column='uHasAvatar')

    objects = models.Manager()

    class Meta:
        db_table = 'Users'
        managed = False

def _wrap_listener(func):
    def get_listener(listener_id, listener_config):
        def listener(sender, **kwargs):
            return func(listener_id, listener_config, sender, **kwargs)

        return listener
    return get_listener

@_wrap_listener
def _get_sync_group_changed_listener(listener_id, config, sender, **kwargs):
    """
    Called if a group is saved, either updating or creating it on the target installation.
    """

    instance = kwargs.get('instance')
    created = kwargs.get('created')

    try:
        gmap = GroupC5Group.objects.get(group=instance, database_id=config['database_id'])

        c5group = C5Group.objects.using(config['database_id']).get(gmap.c5group_id)
        c5group.name = instance.name
        c5group.save()

    except GroupC5Group.DoesNotExist:
        c5group = C5Group.objects.using(config['database_id']).create(name=instance.name, description=u'')

        GroupC5Group.objects.create(group=instance,
                                    c5group_id=c5group.pk,
                                    database_id=config['database_id'])

@_wrap_listener
def _get_sync_group_deleted_listener(listener_id, config, sender, **kwargs):
    """
    Called if a group is deleted, removing all internal references to the
    group but does NOT delete it on the target installation.
    """

    instance = kwargs.get('instance')

    try:
        # TODO: determine delete behaviour
        pass

    except GroupC5Group.DoesNotExist:
        pass

@_wrap_listener
def _get_sync_group_members_listener(listener_id, config, sender, **kwargs):
    """
    Called if changes has been made to the user<=>group association, adding or
    removing users from the groups on all target installations.
    """

    user = kwargs.get('instance')
    action = kwargs.get('action')
    model = kwargs.get('model')
    pk_set = kwargs.get('pk_set')

    if not model is Group:
        # ignore non-group changes.
        return

    if action == 'add':
        for pk in pk_set:
            try:
                gmap = GroupC5Group.objects.get(group__pk=pk, database_id=config['database_id'])

                try:
                    c5user = C5User.objects.using(config['database_id']).get(username=user.username)
                except C5User.DoesNotExist:
                    c5user = C5User.using(config['database_id']).objects.create(username=user.username,
                                                                                email=user.email,
                                                                                date_added=user.date_joined)

                #native_map = NativeUserGroups(native_user.id, map.c5group_id)
                # TODO: Create relation

            except GroupC5Group.DoesNotExist:
                # group not present in concrete5, ignore.
                pass

    elif action == 'remove':
        for pk in pk_set:
            try:
                gmap = GroupC5Group.objects.get(group__pk=pk, database_id=config['database_id'])

                try:
                    native_user = C5User.objects.using(config['database_id']).get(username=user.username)

                    # TODO: Remove relation
                    #native_map = NativeUserGroups.get(session, native_user.id, map.c5group_id)
                    #NativeUserGroups.delete(native_map)
                except C5User.DoesNotExist:
                    pass

            except GroupC5Group.DoesNotExist:
                # group not present in concrete5, ignore.
                pass

    elif action == 'clear':
        #native_user = NativeUsers.get_by_username(session, instance.username)

        #if native_user is not None:
        #    NativeUserGroups.remove_user(session, native_user.id)

        # TODO: remove relations
        pass

listeners = {}
def connect_listeners(listener_id, config):
    global listeners

    connections = [(signals.post_save, _get_sync_group_changed_listener, Group),
                   (signals.pre_delete, _get_sync_group_deleted_listener, Group),
                   (signals.m2m_changed, _get_sync_group_members_listener, User.groups.through)]

    for signal, get_listener_func, sender in connections:
        if not listener_id in listeners:
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

    DatabaseRouter.register_external_table(C5Group, config['database_id'])
    DatabaseRouter.register_external_table(C5User, config['database_id'])