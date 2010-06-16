from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from selvbetjening.notify.proftpd.models import ProftpdGroup, GroupProftpdGroup,\
     registry

class Command(BaseCommand):
    help = 'Inspect proftpd sync status'

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

            proftpdGroups = ProftpdGroup.objects.using(database_id).all()
            synced = GroupProftpdGroup.objects.filter(database_id=database_id)

            self.output('Synchronised:')

            for syncedGroup in synced:
                self.output(syncedGroup.group.name)

            self.output('Un-synchronised groups')

            syncedGroups = [syncedGroup.group for syncedGroup in synced]
            for group in groups:
                if group not in syncedGroups:
                    self.output(group.name)

            self.output('Un-synchronised Proftpd groups')

            syncedGroups = [syncedGroup.proftpdgroup_name for syncedGroup in synced]
            for proftpdGroup in proftpdGroups:
                if proftpdGroup.name not in syncedGroups:
                    self.output(proftpdGroup.name)