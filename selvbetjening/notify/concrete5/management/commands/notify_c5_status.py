from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from selvbetjening.notify.concrete5.models import C5Group, GroupC5Group, registry

class Command(BaseCommand):
    help = 'Inspect C5 synchronisation status'

    def output(self, value):
        if not self._silent:
            print value

    def handle(self, *args, **options):
        groups = Group.objects.all()

        self._silent = 'silent' in args

        for listener_id in registry.listeners:
            config = registry.listeners[listener_id]
            database_id = config['database_id']

            self.output('Status for %s' % listener_id)

            c5groups = C5Group.objects.using(database_id).all()
            synced = GroupC5Group.objects.filter(database_id=database_id)

            self.output('Synchronised:')

            for syncedGroup in synced:
                self.output(syncedGroup.group.name)

            self.output('Un-synchronised groups')

            syncedGroups = [syncedGroup.group for syncedGroup in synced]
            for group in groups:
                if group not in syncedGroups:
                    self.output(group.name)

            self.output('Un-synchronised C5 groups')

            syncedGroups = [syncedGroup.c5group_id for syncedGroup in synced]
            for c5group in c5groups:
                if c5group.pk not in syncedGroups:
                    self.output(c5group.name)