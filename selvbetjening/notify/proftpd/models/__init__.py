import hashlib
import base64

from django.db import models
from django.conf import settings
from django.db.models import signals
from django.contrib.auth.models import Group, User

from selvbetjening.core.database.dbrouter import DatabaseRouter
from selvbetjening.notify import BaseNotifyRegistry
from selvbetjening.data.members.signals import user_changed_username

import listeners # initialize listeners

from native import CompatiblePassword, GroupProftpdGroup
from proftpd import ProftpdGroup, ProftpdUser
from listeners import MemberPasswordChangedListener, \
     GroupMembersChangedListener, UserChangedUsernameListener

class ProftpdNotifyRegistry(BaseNotifyRegistry):
    def __init__(self):
        super(ProftpdNotifyRegistry, self).__init__()

        self._routing = [(signals.m2m_changed,
                          GroupMembersChangedListener,
                          User.groups.through),
                         (signals.post_save,
                          MemberPasswordChangedListener,
                          CompatiblePassword),
                         (user_changed_username,
                          UserChangedUsernameListener,
                          None),]

registry = ProftpdNotifyRegistry()

for listener_id in getattr(settings, 'NOTIFY_PROFTPD', []):
    config = settings.NOTIFY_PROFTPD[listener_id]

    registry.register(listener_id, config)

    DatabaseRouter.register_external_table(ProftpdGroup, config['database_id'])
    DatabaseRouter.register_external_table(ProftpdUser, config['database_id'])