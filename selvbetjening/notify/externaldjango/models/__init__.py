from django.db import models
from django.conf import settings
from django.db.models import signals
from django.contrib.auth.models import Group, User

from selvbetjening.core.database.dbrouter import DatabaseRouter

from selvbetjening.notify import BaseNotifyRegistry
from selvbetjening.data.members.signals import user_changed_username

from native import GroupDjangoGroup
from externaldjango import DjangoGroup, DjangoUser
from listeners import GroupMembersChangedListener, UserChangedUsernameListener

class DjangoNotifyRegistry(BaseNotifyRegistry):
    def __init__(self):
        super(DjangoNotifyRegistry, self).__init__()

        self._routing = [(signals.m2m_changed,
                          GroupMembersChangedListener,
                          User.groups.through),
                         (user_changed_username,
                          UserChangedUsernameListener,
                          None),]

registry = DjangoNotifyRegistry()

for listener_id in getattr(settings, 'NOTIFY_DJANGO', []):
    config = settings.NOTIFY_DJANGO[listener_id]

    registry.register(listener_id, config)

    DatabaseRouter.register_external_table(DjangoGroup, config['database_id'])
    DatabaseRouter.register_external_table(DjangoUser, config['database_id'])