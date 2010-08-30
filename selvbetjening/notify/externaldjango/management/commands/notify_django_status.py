from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from selvbetjening.notify.externaldjango.models import \
     DjangoGroup, GroupDjangoGroup, registry

class Command(BaseCommand):
    help = 'Inspect Django synchronisation status'

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

            djangoGroups = DjangoGroup.objects.using(database_id).all()
            synced = GroupDjangoGroup.objects.filter(database_id=database_id)

            self.output('Synchronised:')

            for syncedGroup in synced:
                self.output(syncedGroup.group.name)

            self.output('Un-synchronised groups')

            syncedGroups = [syncedGroup.group for syncedGroup in synced]
            for group in groups:
                if group not in syncedGroups:
                    self.output(group.name)

            self.output('Un-synchronised Django groups')

            syncedGroups = [syncedGroup.djangogroup_id for syncedGroup in synced]
            for djangoGroup in djangoGroups:
                if djangoGroup.pk not in syncedGroups:
                    self.output(djangoGroup.name)