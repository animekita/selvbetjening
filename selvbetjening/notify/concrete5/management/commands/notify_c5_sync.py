from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from selvbetjening.notify.concrete5.nativemodels import NativeGroups, get_session
from selvbetjening.notify.concrete5.models import GroupsMapper

class Command(BaseCommand):
    help = 'Inspect C5 installations and synchronize groups with Selvbetjening'
    args = '[runsync]'

    def handle(self, *args, **options):
        groups = Group.objects.all()
        dosync = False

        if len(args) > 0 and args[0] == 'runsync':
            dosync = True

        for listener_id in getattr(settings, 'NOTIFY_CONCRETE5', ()):
            config = settings.NOTIFY_CONCRETE5[listener_id]
            session = get_session(config['database_id'])

            print 'Checking %s' % listener_id

            for group in groups:
                try:
                    GroupsMapper.objects.get(group=group,
                                             database_id=config['database_id'])

                except GroupsMapper.DoesNotExist:
                    if dosync:
                        nativegroup = NativeGroups.get_by_name(session, group.name)

                        if nativegroup is None:
                            nativegroup = NativeGroups(group.name, u'')
                            NativeGroups.save(session, nativegroup)

                        GroupsMapper.objects.create(group=group,
                                    native_group_id=nativegroup.id,
                                    database_id=config['database_id'])

                        print 'Group %s created' % group.name

                    else:
                        print 'Group %s not present' % group.name

            session.close()
