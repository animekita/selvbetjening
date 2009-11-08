import fudge

from django.test import TransactionTestCase
from django.contrib.auth.models import Group
from django.db import connection, transaction
from django.conf import settings

from selvbetjening.data.events.tests import Database

import models, nativemodels

class Concrete5BaseTestCase(TransactionTestCase):
    def init_database(self, database_id):
        db_settings = getattr(settings, 'DATABASE_NATIVE', {})
        db_settings[database_id] = {'engine' : 'sqlite', 'name': database_id}
        settings.DATABASE_NATIVE = db_settings

        models.connect_listeners(database_id, {'database_id' : database_id})

        import os
        c5_path = os.path.abspath(os.path.dirname(__file__))

        file = open(os.path.join(c5_path, 'fixtures/nativedb.sql'), 'r')

        connection = nativemodels.get_session(database_id).connection()

        # don't ask how I found that database cursor
        connection.connection.cursor().cursor.executescript(file.read())

        file.close()

    def destroy_database(self, database_id):
        models.disconnect_listeners(database_id)

class Concrete5TestCase(Concrete5BaseTestCase):
    database_id = 'test_c5'

    def setUp(self):
        self.init_database(self.database_id)

    def tearDown(self):
        self.destroy_database(self.database_id)

    def test_add_new_group(self):
        self.assertEqual(models.GroupsMapper.objects.all().count(), 0)
        Group.objects.create(name='test group')
        self.assertEqual(models.GroupsMapper.objects.all().count(), 1)

    def test_remove_group(self):
        self.test_add_new_group()

        group = Group.objects.all()[0]
        group.delete()

        self.assertEqual(models.GroupsMapper.objects.all().count(), 0)

    def test_add_user(self):
        self.test_add_new_group()

        group = Group.objects.all()[0]

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        session = nativemodels.get_session(self.database_id)

        native_group = nativemodels.NativeGroups.get(session, group.id)
        native_user1 = nativemodels.NativeUsers.get_by_username(session, user1.username)
        native_user2 = nativemodels.NativeUsers.get_by_username(session, user2.username)

        native_ug1 = nativemodels.NativeUserGroups.get(session, native_user1.id, native_group.id)
        native_ug2 = nativemodels.NativeUserGroups.get(session, native_user2.id, native_group.id)

        self.assertEqual(native_ug1.uID, native_user1.id)
        self.assertEqual(native_ug2.gID, group.id)

    def test_remove_user(self):
        self.test_add_user()

class Concrete5MultipleInstancesTestCase(Concrete5BaseTestCase):
    def setUp(self):
        self.init_database('test_c53')
        self.init_database('test_c52')

    def tearDown(self):
        self.destroy_database('test_c53')
        self.destroy_database('test_c52')

    def test_add_user(self):
        group = Group.objects.create(name='test group')

        self.assertEqual(models.GroupsMapper.objects.all().count(), 2)

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        def check_database(database_id):
            session = nativemodels.get_session(database_id)

            native_group = nativemodels.NativeGroups.get(session, group.id)
            native_user1 = nativemodels.NativeUsers.get_by_username(session, user1.username)
            native_user2 = nativemodels.NativeUsers.get_by_username(session, user2.username)

            native_ug1 = nativemodels.NativeUserGroups.get(session, native_user1.id, native_group.id)
            native_ug2 = nativemodels.NativeUserGroups.get(session, native_user2.id, native_group.id)

            self.assertEqual(native_ug1.uID, native_user1.id)
            self.assertEqual(native_ug2.gID, group.id)

        check_database('test_c53')
        check_database('test_c52')



