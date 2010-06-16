from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from selvbetjening.notify.proftpd.models import ProftpdGroup, GroupProftpdGroup,\
     registry

class Command(BaseCommand):
    help = 'Manage proftpd sync'
    args = 'add|remove proftpd_group_name selvbetjening_group_name'

    def handle(self, *args, **options):
        action = args[0]
        proftpdGroupName = args[1]
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
                proftpdGroup = ProftpdGroup.objects.using(database_id).\
                                                    get(name=proftpdGroupName)
            except ProftpdGroup.DoesNotExist:
                raise CommandError('A proftpd group with the given name could not be found')

            if action == 'add':
                association, created = GroupProftpdGroup.objects.get_or_create(
                    proftpdgroup_name=proftpdGroupName,
                    database_id=database_id,
                    defaults={'group' : group})

                if not created:
                    association.group = group
                    association.save()

            elif action == 'remove':
                try:
                    association = GroupProftpdGroup.objects.get(
                        group=group,
                        proftpdgroup_name=proftpdGroupName,
                        database_id=database_id)

                    association.delete()
                except GroupProftpdGroup.DoesNotExist:
                    pass
