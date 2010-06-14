from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from selvbetjening.notify.proftpd.nativemodels import NativeGroups, NativeUsers, get_session
from selvbetjening.notify.proftpd.models import GroupsMapper, CompatiblePassword, add_or_update_user

class Command(BaseCommand):
    help = 'Inspect proftpd installations and synchronize groups with Selvbetjening'
    args = '[runsync]'

    def handle(self, *args, **options):
        groups = Group.objects.all()
        dosync = False

        if len(args) > 0 and args[0] == 'runsync':
            dosync = True

        for listener_id in getattr(settings, 'NOTIFY_PROFTPD', ()):
            config = settings.NOTIFY_PROFTPD[listener_id]
            session = get_session(config['database_id'])

            print 'Checking %s' % listener_id

            for group in groups:
                # sync group
                try:
                    map = GroupsMapper.objects.get(group=group,
                                                   database_id=config['database_id'])

                except GroupsMapper.DoesNotExist:
                    if dosync:
                        nativegroup = NativeGroups.get_by_name(session, group.name)

                        if nativegroup is None:
                            nativegroup = NativeGroups(unicode(group.name), config['default_gid'], u'')
                            NativeGroups.save(session, nativegroup)

                        map = GroupsMapper.objects.create(group=group,
                                                          native_group_name=group.name,
                                                          database_id=config['database_id'])

                        print 'Group %s created' % group.name

                    else:
                        print 'Group %s not present' % group.name

                # sync group members
                if dosync:
                    print 'Updating user list for group %s' % group.name

                    for user in group.user_set.all():
                        add_or_update_user(user, group, session, config)

            session.close()
