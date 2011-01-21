from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from selvbetjening.notify.vanillaforum.models import RemoteUserAssociation, RemoteUser

class Command(BaseCommand):
    help = 'Synchronise vanilla forum with selvbetjening'
    args = '[sync]'

    def handle(self, *args, **options):
        for instance_id in getattr(settings, 'NOTIFY_VANILLAFORUM', []):
            config = settings.NOTIFY_VANILLAFORUM[instance_id]

            do_sync = (len(args) == 1 and args[0] == 'sync')
            self.sync(config['database_id'], do_sync)

    def sync(self, database_id, do_sync):
        print 'Status for database %s' % database_id
        print ''

        print 'User Sync Status'
        synced_users = RemoteUser.objects.using(database_id).values_list('username', flat=True)
        unsynced_users_count = User.objects.exclude(username__in=list(synced_users)).count()

        if unsynced_users_count == 0:
            print 'OK'
        else:
            print 'UNSYNCED! Please sync immediately (not implemented)'

        print 'Remote User Association Sync Status'
        synced_user_ids = RemoteUserAssociation.objects.using(database_id)\
                                                       .all()\
                                                       .values_list('selv_user_id', flat=True)

        unsynced_users = User.objects.exclude(pk__in=list(synced_user_ids))

        if len(unsynced_users) == 0:
            print 'OK'
        elif not do_sync:
            print 'UNSYNCED! Please sync immediately'
        else:
            for unsynced_user in unsynced_users:
                remote_user = RemoteUser.objects.using(database_id)\
                                                .get(username=unsynced_user.username)

                RemoteUserAssociation.objects.using(database_id)\
                                             .create(selv_user_id=unsynced_user.pk,
                                                     remote_user_id=remote_user.id)
                print '.',

            print ' Synced!'

        print 'Group Sync Status'
        print '<not implemented>'