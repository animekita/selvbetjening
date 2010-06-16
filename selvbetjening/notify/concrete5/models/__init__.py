from django.db import models
from django.conf import settings
from django.db.models import signals
from django.contrib.auth.models import Group, User

from selvbetjening.core.database.dbrouter import DatabaseRouter

from selvbetjening.notify import BaseNotifyRegistry

from native import GroupC5Group
from concrete5 import C5Group, C5User, C5UserGroups
from listeners import GroupMembersChangedListener

class C5NotifyRegistry(BaseNotifyRegistry):
    def __init__(self):
        super(C5NotifyRegistry, self).__init__()

        self._routing = [(signals.m2m_changed,
                          GroupMembersChangedListener,
                          User.groups.through),]

registry = C5NotifyRegistry()

for listener_id in getattr(settings, 'NOTIFY_CONCRETE5', []):
    config = settings.NOTIFY_CONCRETE5[listener_id]

    registry.register(listener_id, config)

    DatabaseRouter.register_external_table(C5Group, config['database_id'])
    DatabaseRouter.register_external_table(C5User, config['database_id'])
    DatabaseRouter.register_external_table(C5UserGroups, config['database_id'])