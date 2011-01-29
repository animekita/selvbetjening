import hashlib
import random

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models import F

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
        unsynced_users = User.objects.exclude(username__in=list(synced_users))

        if unsynced_users.count() == 0:
            print 'OK'
        elif not do_sync:
            print 'UNSYNCED! Please sync immediately'
        else:
            for user in unsynced_users:
                random_pass = hashlib.sha1(str(random.randint(0, 99999999))).hexdigest()

                RemoteUser.objects.using(database_id)\
                                  .create(username=user.username,
                                          password=random_pass,
                                          email=user.email)

                print 'User %s created in vanilla' % user.username


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
            ignored_users = []
            for unsynced_user in unsynced_users:
                try:
                    remote_user = RemoteUser.objects.using(database_id)\
                                                    .get(username=unsynced_user.username)

                    RemoteUserAssociation.objects.using(database_id)\
                                                 .create(selv_user_id=unsynced_user.pk,
                                                         remote_user_id=remote_user.id)

                    print '.',
                except RemoteUser.DoesNotExist:
                    ignored_users.append(unsynced_user)

            for user in ignored_users:
                print 'Skipping %s due to missing user account' % user.username

            print ' Synced!'


        print 'Group Sync Status'
        print '<not implemented>'

        print 'Date Sync Status'

        users_high_registration_date = RemoteUser.objects.using(database_id)\
                                                 .filter(first_visit_date__lt=F('registration_date'))

        users_no_registration_date = RemoteUser.objects.using(database_id)\
                                                       .filter(registration_date=None)

        if users_high_registration_date.count() == 0 and users_no_registration_date.count() == 0:
            print 'OK'
        elif not do_sync:
            print 'UNSYNCED! Please sync immediately'
        else:
            for user in users_high_registration_date:
                user.registration_date = user.first_visit_date
                user.save()

                print '.',

            print ''

            skipped_users = []

            for user in users_no_registration_date:
                try:
                    association = RemoteUserAssociation.objects.using(database_id)\
                                                               .get(remote_user_id=user.id)

                    local_user = User.objects.get(pk=association.selv_user_id)

                    user.registration_date = local_user.date_joined
                    user.save()

                    print '.',

                except RemoteUserAssociation.DoesNotExist:
                    skipped_users.append(user)

            print 'Synced!'

            for user in skipped_users:
                print 'Skipping %s due to missing association' % user.username
