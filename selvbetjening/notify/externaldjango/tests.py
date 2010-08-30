from django.contrib.auth.models import Group
from django.core.management.base import CommandError

from selvbetjening.data.events.tests import Database
from selvbetjening.notify.tests import BaseNotifyTestCase

from models import GroupDjangoGroup, DjangoGroup, DjangoUser, registry
from management.commands import notify_django_status, notify_django_manage

class DjangoBaseTestCase(BaseNotifyTestCase):
    _active_test_file = __file__

    def register_notify(self, database_id):
        registry.register(database_id, {'database_id' : database_id})

    def unregister_notify(self, database_id):
        registry.unregister(database_id)

class DjangoGroupTestCase(DjangoBaseTestCase):
    def test_get_group_special_syntax(self):
        """
        Get a group using the special syntax
        """

        group = Group.objects.create(name='test group')

        def setup(database_id):
            djangoGroup = DjangoGroup.objects.using(database_id).\
                                              create(name='TestGroup')

            GroupDjangoGroup.objects.create(group=group,
                                            djangogroup_id=djangoGroup.pk,
                                            database_id=database_id)

        self.check_databases(setup)

        def check(database_id):
            djangoGroup = DjangoGroup.objects.get(group=group,
                                                  database_id=database_id)

            self.assertRaises(DjangoGroup.DoesNotExist, DjangoGroup.objects.get,
                              group=100, database_id=database_id)

        self.check_databases(check)

class DjangoUserTestCase(DjangoBaseTestCase):
    def test_add_user(self):
        """
        Add new user

        Check that user is created in Django and associated with
        the correct groups
        """

        group = Group.objects.create(name='test group')

        def setup(database_id):
            djangoGroup = DjangoGroup.objects.using(database_id).\
                                              create(name='TestGroup')

            GroupDjangoGroup.objects.create(group=group,
                                            djangogroup_id=djangoGroup.pk,
                                            database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        def check(database_id):
            self.assertEqual(2,
                             DjangoUser.objects.\
                             using(database_id).\
                             all().\
                             count())

            djangoGroup = DjangoGroup.objects.using(database_id).\
                                              get(pk=group.pk)

            self.assertEqual(2, djangoGroup.user_set.count())

        self.check_databases(check)

    def test_remove_user(self):
        """
        Remove a user from a group

        Check that the user relation is removed from django
        """

        group = Group.objects.create(name='test group')

        def setup(database_id):
            djangoGroup = DjangoGroup.objects.using(database_id).\
                                              create(name='TestGroup')

            GroupDjangoGroup.objects.create(group=group,
                                            djangogroup_id=djangoGroup.pk,
                                            database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        user1.groups.remove(group)

        def check(database_id):
            djangoGroup = DjangoGroup.objects.get(group=group,
                                                  database_id=database_id)

            self.assertEqual(1, djangoGroup.user_set.count())

        self.check_databases(check)

    def test_clear_users(self):
        """
        Clear groups from a user

        Check that the user relations are removed from django
        """

        group = {}
        group[0] = Group.objects.create(name='test group1')
        group[1] = Group.objects.create(name='test group2')

        def setup(database_id):
            for x in xrange(0,2):
                djangoGroup = DjangoGroup.objects.using(database_id).\
                                                  create(name='TestGroup%s' % x)

                GroupDjangoGroup.objects.create(group=group[x],
                                                djangogroup_id=djangoGroup.pk,
                                                database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()

        user1.groups.add(group[0])
        user1.groups.add(group[1])

        user1.groups.clear()

        def check(database_id):
            djangoUser = DjangoUser.objects.using(database_id).\
                                            get(username=user1.username)

            self.assertEqual(0, djangoUser.groups.count())

        self.check_databases(check)

    def test_rename_user(self):
        group = Group.objects.create(name='test group')

        def setup(database_id):
            djangoGroup = DjangoGroup.objects.using(database_id).\
                                                    create(name='TestGroup')

            GroupDjangoGroup.objects.create(group=group,
                                            djangogroup_id=djangoGroup.pk,
                                            database_id=database_id)

        self.check_databases(setup)

        user = Database.new_user()

        user.groups.add(group)

        user.username = 'brand_new_username'
        user.save()

        def check(database_id):
            self.assertEqual(1,
                             DjangoUser.objects.\
                                        using(database_id).\
                                        filter(username='brand_new_username').\
                                        count())

        self.check_databases(check)

class DjangoManagementTestCase(DjangoBaseTestCase):
    def test_add_relation_wrong_groups(self):
        command = notify_django_manage.Command()

        self.assertRaises(CommandError, command.handle,
                          'add', 'testgroup', 'testgroup')

    def test_add_relation(self):
        group = Group.objects.create(name='TestGroup')

        def setup(database_id):
            djangoGroup = DjangoGroup.objects.using(database_id).\
                                              create(name='TestGroup')

        self.check_databases(setup)

        command = notify_django_manage.Command()
        command.handle('add', 'TestGroup', 'TestGroup')

        def check(database_id):
            self.assertEqual(1,
                             GroupDjangoGroup.objects.\
                             filter(database_id=database_id).count())

        self.check_databases(check)

    def test_remove_relation(self):
        group = Group.objects.create(name='TestGroup')

        def setup(database_id):
            djangoGroup = DjangoGroup.objects.using(database_id).\
                                              create(name='TestGroup')

            GroupDjangoGroup.objects.create(group=group,
                                            djangogroup_id=djangoGroup.pk,
                                            database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        command = notify_django_manage.Command()
        command.handle('remove', 'TestGroup', 'TestGroup')

        def check(database_id):
            self.assertRaises(DjangoGroup.DoesNotExist,
                              DjangoGroup.objects.get,
                              group=group,
                              database_id=database_id)

        self.check_databases(check)

    def test_management_status(self):
        command = notify_django_status.Command()
        command.handle('silent')
