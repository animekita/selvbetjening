from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User

from selvbetjening.core.database.dbrouter import DatabaseRouter
from selvbetjening.notify import BaseNotifyRegistry

from listeners import UserChangedListener, UserDeletedListener
from remote import RemoteUserAssociation, RemoteUser

class VanillaForumRegistry(BaseNotifyRegistry):
    def __init__(self):
        super(VanillaForumRegistry, self).__init__()

        self._routing = [(post_save,
                          UserChangedListener,
                          User),
                         (post_delete,
                          UserDeletedListener,
                          User)]

registry = VanillaForumRegistry()

for instance_id in getattr(settings, 'NOTIFY_VANILLAFORUM', []):
    config = settings.NOTIFY_VANILLAFORUM[instance_id]

    registry.register(instance_id, config)

    DatabaseRouter.register_external_table(RemoteUserAssociation, config['database_id'])
    DatabaseRouter.register_external_table(RemoteUser, config['database_id'])