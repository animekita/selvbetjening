from django.test import TransactionTestCase
from django.contrib.auth.models import Group

from selvbetjening.data.events.tests import Database
from selvbetjening.notify.tests import BaseNotifyTestCase

from models import GroupC5Group, C5Group, C5User, C5UserGroups, registry

class Concrete5BaseTestCase(BaseNotifyTestCase):
    _active_test_file = __file__

    def register_notify(self, database_id):
        registry.register(database_id, {'database_id' : database_id})

    def unregister_notify(self, database_id):
        registry.unregister(database_id)

class Concrete5GroupTestCase(Concrete5BaseTestCase):
    def test_add_new_group(self):
        """
        Add new group

        Check that an identical group is created in C5
        """

        self.assertEqual(GroupC5Group.objects.all().count(), 0)

        Group.objects.create(name='test group')

        def check(database_id):
            self.assertEqual(1,
                             GroupC5Group.objects.\
                             filter(database_id=database_id).\
                             count())

            self.assertEqual(1,
                             C5Group.objects.\
                             using(database_id).\
                             all().\
                             count())

        self.check_databases(check)

    def test_remove_group(self):
        """
        Remove group

        Check that the group is NOT removed from C5
        """

        group = Group.objects.create(name='test group')
        group.delete()

        def check(database_id):
            self.assertEqual(0,
                             GroupC5Group.objects.\
                             filter(database_id=database_id).\
                             count())

            self.assertEqual(1,
                             C5Group.objects.\
                             using(database_id).\
                             all().\
                             count())

        self.check_databases(check)

    def test_modify_group(self):
        """
        Make changes to a group

        Check that chages are propagated to C5
        """

        group = Group.objects.create(name='test group')

        def check(database_id):
            c5group = C5Group.objects.\
                      get(group=group, database_id=database_id)

            self.assertEqual(group.name, c5group.name)

        self.check_databases(check)

        group.name = 'new name'
        group.save()

        self.check_databases(check)

    def test_get_group_special_syntax(self):
        """
        Get a group using the special syntax
        """

        group = Group.objects.create(name='test group')

        def check(database_id):
            c5group = C5Group.objects.get(group=group, database_id=database_id)
            self.assertEqual(group.name, c5group.name)

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

            groupc5group = GroupC5Group.objects.\
                           get(group=group, database_id=database_id)

            c5group = C5Group.objects.\
                      using(database_id).\
                      get(pk=groupc5group.c5group_id)

            self.assertEqual(2, c5group.users.count())

        self.check_databases(check)

    def test_remove_user(self):
        """
        Remove a user from a group

        Check that the user relation is removed from C5
        """

        group = Group.objects.create(name='test group')

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

        group1 = Group.objects.create(name='test group1')
        group2 = Group.objects.create(name='test group2')

        user1 = Database.new_user()

        user1.groups.add(group1)
        user1.groups.add(group2)

        user1.groups.clear()

        def check(database_id):
            self.assertEqual(0,
                             C5UserGroups.objects.\
                                          using(database_id).\
                                          all().\
                                          count())

        self.check_databases(check)
