from django.test import TransactionTestCase
from django.contrib.auth.models import Group
from django.conf import settings

from selvbetjening.data.events.tests import Database

import models, nativemodels

class ProftpdBaseTestCase(TransactionTestCase):
    def init_database(self, database_id):
        db_settings = getattr(settings, 'DATABASE_NATIVE', {})
        db_settings[database_id] = {'engine' : 'sqlite', 'name': database_id}
        settings.DATABASE_NATIVE = db_settings

        models.connect_listeners(database_id, {'database_id': database_id,
              'username_format': '%s@test',
              'default_uid': 3000,
              'default_gid': 3000,
              'ftp_dir': '/home/'})

        import os
        c5_path = os.path.abspath(os.path.dirname(__file__))

        file = open(os.path.join(c5_path, 'fixtures/nativedb.sql'), 'r')

        connection = nativemodels.get_session(database_id).connection()

        # don't ask how I found that database cursor
        connection.connection.cursor().cursor.executescript(file.read())

        file.close()

    def destroy_database(self, database_id):
        models.disconnect_listeners(database_id)

class ProftpdTestCase(ProftpdBaseTestCase):
    database_id = 'test_proftpd'

    def setUp(self):
        self.init_database(self.database_id)

    def tearDown(self):
        self.destroy_database(self.database_id)

    def test_add_new_group(self):
        self.assertEqual(models.GroupsMapper.objects.all().count(), 0)
        Group.objects.create(name='TestGroup')
        self.assertEqual(models.GroupsMapper.objects.all().count(), 1)

    def test_remove_group(self):
        self.test_add_new_group()

        group = Group.objects.all()[0]
        group.delete()

        self.assertEqual(models.GroupsMapper.objects.all().count(), 0)

    def test_add_user_with_password(self):
        self.test_add_new_group()

        group = Group.objects.all()[0]

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        session = nativemodels.get_session(self.database_id)

        native_group = nativemodels.NativeGroups.get_by_name(session, group.name)
        native_user1 = nativemodels.NativeUsers.get_by_username(session, '%s@test' % user1.username)
        native_user2 = nativemodels.NativeUsers.get_by_username(session, '%s@test' % user2.username)

        self.assertNotEqual(native_group, None)
        self.assertNotEqual(native_user1, None)
        self.assertNotEqual(native_user2, None)

    def test_add_user_no_password(self):
        self.test_add_new_group()

        group = Group.objects.all()[0]

        user1 = Database.new_user()

        user1.groups.add(group)

        session = nativemodels.get_session(self.database_id)

        native_group = nativemodels.NativeGroups.get_by_name(session, group.name)
        native_user1 = nativemodels.NativeUsers.get_by_username(session, user1.username)

        self.assertNotEqual(native_group, None)
        self.assertEqual(native_user1, None)

class ProftpdMultipleInstancesTestCase(ProftpdBaseTestCase):
    def setUp(self):
        self.init_database('test_pro1')
        self.init_database('test_pro2')

    def tearDown(self):
        self.destroy_database('test_pro1')
        self.destroy_database('test_pro2')

    def test_add_user(self):
        group = Group.objects.create(name='TestGroup')

        self.assertEqual(models.GroupsMapper.objects.all().count(), 2)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        def check_database(database_id):
            session = nativemodels.get_session(database_id)

            native_group = nativemodels.NativeGroups.get_by_name(session, group.name)
            native_user1 = nativemodels.NativeUsers.get_by_username(session, '%s@test' % user1.username)
            native_user2 = nativemodels.NativeUsers.get_by_username(session, '%s@test' % user2.username)

            self.assertNotEqual(native_group, None)
            self.assertNotEqual(native_user1, None)
            self.assertNotEqual(native_user2, None)

        check_database('test_pro1')
        check_database('test_pro2')

class TestSetCompatPassword(TransactionTestCase):
    def test_set_new_password(self):
        user1 = Database.new_user()

        cp1 = models.CompatiblePassword.objects.get(user=user1)

        user1.set_password('newpassword')

        cp2 = models.CompatiblePassword.objects.get(user=user1)

        self.assertNotEqual(cp1.password, cp2.password)


