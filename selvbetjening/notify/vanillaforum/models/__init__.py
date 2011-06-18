from django.conf import settings
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.contrib.auth.models import User

from selvbetjening.core.database.dbrouter import DatabaseRouter
from selvbetjening.notify import BaseNotifyRegistry

from remote import RemoteUserAssociation, RemoteUser, RemoteRole, RemoteUserRole
from listeners import UserChangedListener, UserDeletedListener, \
     SettingsChangedListener, GroupMembersChangedListener, register_new_user,\
     update_user_settings

from native import Settings, GroupRemoteRole

class VanillaForumRegistry(BaseNotifyRegistry):
    def __init__(self):
        super(VanillaForumRegistry, self).__init__()

        self._routing = [(post_save,
                          UserChangedListener,
                          User),
                         (post_delete,
                          UserDeletedListener,
                          User),
                         (post_save,
                          SettingsChangedListener,
                          Settings),
                         (m2m_changed,
                          GroupMembersChangedListener,
                          User.groups.through)]

registry = VanillaForumRegistry()

for instance_id in getattr(settings, 'NOTIFY_VANILLAFORUM', []):
    config = settings.NOTIFY_VANILLAFORUM[instance_id]

    registry.register(instance_id, config)

    DatabaseRouter.register_external_table(RemoteUserAssociation, config['database_id'])
    DatabaseRouter.register_external_table(RemoteUser, config['database_id'])