from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from selvbetjening.notify.concrete5.models import C5Group, GroupC5Group, registry

class Command(BaseCommand):
    help = 'Manage C5 sync'
    args = 'add|remove c5_group_name selvbetjening_group_name'

    def handle(self, *args, **options):
        action = args[0]
        c5GroupName = args[1]
        groupName = args[2]

        if action not in ['add', 'remove']:
            raise CommandError('Command should be either add or remove')

        try:
            group = Group.objects.get(name=groupName)
        except Group.DoesNotExist:
            raise CommandError('A group with the given name could not be found')

        for listener_id in registry.listeners:
            config = registry.listeners[listener_id]
            database_id = config['database_id']

            try:
                c5Group = C5Group.objects.using(database_id).\
                                          get(name=c5GroupName)
            except C5Group.DoesNotExist:
                raise CommandError('A C5 group with the given name could not be found')

            if action == 'add':
                association, created = GroupC5Group.objects.get_or_create(
                    c5group_id=c5Group.pk,
                    database_id=database_id,
                    defaults={'group' : group})

                if not created:
                    association.group = group
                    association.save()

            elif action == 'remove':
                try:
                    association = GroupC5Group.objects.get(
                        group=group,
                        c5group_id=c5Group.pk,
                        database_id=database_id)

                    association.delete()
                except GroupProftpdGroup.DoesNotExist:
                    pass