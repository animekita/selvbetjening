from django.contrib.auth.models import Group
from django.core.management.base import CommandError

from selvbetjening.data.events.tests import Database
from selvbetjening.notify.tests import BaseNotifyTestCase

from models import GroupC5Group, C5Group, C5User, C5UserGroups, registry
from management.commands import notify_c5_status, notify_c5_manage

class Concrete5BaseTestCase(BaseNotifyTestCase):
    _active_test_file = __file__

    def register_notify(self, database_id):
        registry.register(database_id, {'database_id' : database_id})

    def unregister_notify(self, database_id):
        registry.unregister(database_id)

class Concrete5GroupTestCase(Concrete5BaseTestCase):
    def test_get_group_special_syntax(self):
        """
        Get a group using the special syntax
        """

        group = Group.objects.create(name='test group')

        def setup(database_id):
            c5Group = C5Group.objects.using(database_id).\
                                            create(name='TestGroup',
                                                   description='')

            GroupC5Group.objects.create(group=group,
                                        c5group_id=c5Group.pk,
                                        database_id=database_id)

        self.check_databases(setup)

        def check(database_id):
            c5group = C5Group.objects.get(group=group, database_id=database_id)

            self.assertRaises(C5Group.DoesNotExist, C5Group.objects.get,
                              group=100, database_id=database_id)

        self.check_databases(check)

class Concrete5UserTestCase(Concrete5BaseTestCase):
    def test_add_user(self):
        """
        Add new user

        Check that user is created in C5 and associated with
        the correct groups
        """

        group = Group.objects.create(name='test group')

        def setup(database_id):
            c5Group = C5Group.objects.using(database_id).\
                                            create(name='TestGroup',
                                                   description='')

            GroupC5Group.objects.create(group=group,
                                        c5group_id=c5Group.pk,
                                        database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        def check(database_id):
            self.assertEqual(2,
                             C5User.objects.\
                             using(database_id).\
                             all().\
                             count())

            c5group = C5Group.objects.get(group=group,
                                          database_id=database_id)

            self.assertEqual(2, c5group.users.count())

        self.check_databases(check)

    def test_remove_user(self):
        """
        Remove a user from a group

        Check that the user relation is removed from C5
        """

        group = Group.objects.create(name='test group')

        def setup(database_id):
            c5Group = C5Group.objects.using(database_id).\
                                            create(name='TestGroup',
                                                   description='')

            GroupC5Group.objects.create(group=group,
                                        c5group_id=c5Group.pk,
                                        database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        user1.groups.remove(group)

        def check(database_id):
            self.assertEqual(1,
                             C5UserGroups.objects.\
                                          using(database_id).\
                                          all().\
                                          count())

        self.check_databases(check)

    def test_clear_users(self):
        """
        Clear groups from a user

        Check that the user relations are removed from C5
        """

        group = {}
        group[0] = Group.objects.create(name='test group1')
        group[1] = Group.objects.create(name='test group2')

        def setup(database_id):
            for x in xrange(0,2):
                c5Group = C5Group.objects.using(database_id).\
                                          create(name='TestGroup%s' % x,
                                                 description='')

                GroupC5Group.objects.create(group=group[x],
                                        c5group_id=c5Group.pk,
                                        database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()

        user1.groups.add(group[0])
        user1.groups.add(group[1])

        user1.groups.clear()

        def check(database_id):
            self.assertEqual(0,
                             C5UserGroups.objects.\
                                          using(database_id).\
                                          all().\
                                          count())

        self.check_databases(check)

class Concrete5ManagementTestCase(Concrete5BaseTestCase):
    def test_add_relation_wrong_groups(self):
        command = notify_c5_manage.Command()

        self.assertRaises(CommandError, command.handle,
                          'add', 'testgroup', 'testgroup')

    def test_add_relation(self):
        group = Group.objects.create(name='TestGroup')

        def setup(database_id):
            c5Group = C5Group.objects.using(database_id).\
                                      create(name='TestGroup',
                                             description='')

        self.check_databases(setup)

        command = notify_c5_manage.Command()
        command.handle('add', 'TestGroup', 'TestGroup')

        def check(database_id):
            self.assertEqual(1,
                             GroupC5Group.objects.\
                             filter(database_id=database_id).count())

        self.check_databases(check)

    def test_remove_relation(self):
        group = Group.objects.create(name='TestGroup')

        def setup(database_id):
            c5Group = C5Group.objects.using(database_id).\
                                      create(name='TestGroup',
                                             description='')

            GroupC5Group.objects.create(group=group,
                                        c5group_id=c5Group.pk,
                                        database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        command = notify_c5_manage.Command()
        command.handle('remove', 'TestGroup', 'TestGroup')

        def check(database_id):
            self.assertRaises(C5Group.DoesNotExist,
                              C5Group.objects.get,
                              group=group,
                              database_id=database_id)

        self.check_databases(check)

    def test_management_status(self):
        command = notify_c5_status.Command()
        command.handle()
