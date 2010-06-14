from django.test import TransactionTestCase
from django.contrib.auth.models import Group
from django.conf import settings

from selvbetjening.data.events.tests import Database
from selvbetjening.notify.tests import BaseNotifyTestCase

from models import registry, ProftpdGroup, ProftpdUser, GroupProftpdGroup,\
     CompatiblePassword

USERNAME_FORMAT = '%s@test'

class ProftpdBaseTestCase(BaseNotifyTestCase):
    _active_test_file = __file__

    def register_notify(self, database_id):
        registry.register(database_id, {'database_id' : database_id,
                                        'username_format': USERNAME_FORMAT,
                                        'default_uid': 3000,
                                        'default_gid': 3000,
                                        'ftp_dir': '/home/'})

    def unregister_notify(self, database_id):
        registry.unregister(database_id)

class ProftpdGroupTestCase(ProftpdBaseTestCase):
    def test_remove_group(self):
        """
        Group is removed and with it all user associations
        but the proftpd group itself is not removed.
        """

        Group.objects.create(name='TestGroup')

        def check(database_id):
            pass

        self.check_databases(check)

        self.fail("write test")

class ProftpdUserTestCase(ProftpdBaseTestCase):
    def test_add_user_to_group(self):
        """
        Add a user to a proftpd associated group

        Check that the user is correctly created in proftpd
        and associated with a group
        """

        group = Group.objects.create(name='TestGroup')

        def setup(database_id):
            proftpdGroup = ProftpdGroup.objects.using(database_id).\
                                                create(name='TestGroup',
                                                       gid=3000)

            GroupProftpdGroup.objects.create(group=group,
                                             proftpdgroup_name=proftpdGroup.name,
                                             database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        def check(database_id):
            self.assertEqual(2, ProftpdUser.objects.using(database_id).count())
            proftpdGroup = ProftpdGroup.objects.get(group=group,
                                                    database_id=database_id)

            self.assertTrue(proftpdGroup.is_member(USERNAME_FORMAT % user1.username))
            self.assertTrue(proftpdGroup.is_member(USERNAME_FORMAT % user2.username))

        self.check_databases(check)

    def test_remove_user_from_group(self):
        """
        Create groups and users. Then remove a group from a user.

        Check that the user is removed from the proftpd group.
        """

        group = Group.objects.create(name='TestGroup')

        def setup(database_id):
            proftpdGroup = ProftpdGroup.objects.using(database_id).\
                                                create(name='TestGroup',
                                                       gid=3000)

            GroupProftpdGroup.objects.create(group=group,
                                             proftpdgroup_name=proftpdGroup.name,
                                             database_id=database_id)

        self.check_databases(setup)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        user1.groups.clear()

        def check(database_id):
            self.assertEqual(2, ProftpdUser.objects.using(database_id).count())
            proftpdGroup = ProftpdGroup.objects.get(group=group,
                                                    database_id=database_id)

            self.assertFalse(proftpdGroup.is_member(USERNAME_FORMAT % user1.username))
            self.assertTrue(proftpdGroup.is_member(USERNAME_FORMAT % user2.username))

        self.check_databases(check)

class TestSetCompatPassword(TransactionTestCase):
    def test_set_new_password(self):
        user1 = Database.new_user()

        cp1 = CompatiblePassword.objects.get(user=user1)

        user1.set_password('newpassword')

        cp2 = CompatiblePassword.objects.get(user=user1)

        self.assertNotEqual(cp1.password, cp2.password)


