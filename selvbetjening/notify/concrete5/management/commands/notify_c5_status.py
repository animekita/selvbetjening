from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from selvbetjening.notify.concrete5.models import C5Group, GroupC5Group, registry

class Command(BaseCommand):
    help = 'Inspect C5 synchronisation status'

    def handle(self, *args, **options):
        groups = Group.objects.all()

        for listener_id in registry.listeners:
            config = registry.listeners[listener_id]
            database_id = config['database_id']

            print 'Status for %s' % listener_id

            c5groups = C5Group.objects.using(database_id).all()
            synced = GroupC5Group.objects.filter(database_id=database_id)

            print 'Synchronised:'

            for syncedGroup in synced:
                print syncedGroup.group.name

            print 'Un-synchronised groups'

            syncedGroups = [syncedGroup.group for syncedGroup in synced]
            for group in groups:
                if group not in syncedGroups:
                    print group.name

            print 'Un-synchronised C5 groups'

            syncedGroups = [syncedGroup.c5group_id for syncedGroup in synced]
            for c5group in c5groups:
                if c5group.pk not in syncedGroups:
                    print c5group.name