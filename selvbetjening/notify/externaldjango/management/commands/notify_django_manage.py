from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from selvbetjening.notify.externaldjango.models import \
     DjangoGroup, GroupDjangoGroup, registry

class Command(BaseCommand):
    help = 'Manage Django sync'
    args = 'add|remove django_group_name selvbetjening_group_name'

    def handle(self, *args, **options):
        action = args[0]
        djangoGroupName = args[1]
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
                djangoGroup = DjangoGroup.objects.using(database_id).\
                                                  get(name=djangoGroupName)
            except DjangoGroup.DoesNotExist:
                raise CommandError('A Django group with the given name could not be found')

            if action == 'add':
                association, created = GroupDjangoGroup.objects.get_or_create(
                    djangogroup_id=djangoGroup.pk,
                    database_id=database_id,
                    defaults={'group' : group})

                if not created:
                    association.group = group
                    association.save()

            elif action == 'remove':
                try:
                    association = GroupDjangoGroup.objects.get(
                        group=group,
                        djangogroup_id=djangoGroup.pk,
                        database_id=database_id)

                    association.delete()
                except GroupDjangoGroup.DoesNotExist:
                    pass