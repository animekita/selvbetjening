from django.test import TransactionTestCase
from django.contrib.auth.models import Group
from django.db import connections

from selvbetjening.data.events.tests import Database

import models

class Concrete5BaseTestCase(TransactionTestCase):
    def init_database(self, database_id):
        models.connect_listeners(database_id, {'database_id' : database_id})

        import os
        c5_path = os.path.abspath(os.path.dirname(__file__))

        sqlfile = open(os.path.join(c5_path, 'fixtures/nativedb.sql'), 'r')

        cursor = connections['intranet'].cursor()

        cursor.executescript(sqlfile.read())

        sqlfile.close()

    def destroy_database(self, database_id):
        models.disconnect_listeners(database_id)

class Concrete5TestCase(Concrete5BaseTestCase):
    def setUp(self):
        self.init_database('intranet')

    def tearDown(self):
        self.destroy_database('intranet')

    def test_add_new_group(self):
        self.assertEqual(models.GroupC5Group.objects.all().count(), 0)

        Group.objects.create(name='test group')

        self.assertEqual(models.GroupC5Group.objects.all().count(), 1)
        self.assertEqual(models.C5Group.objects.all().count(), 1)

    def test_remove_group(self):
        self.test_add_new_group()

        group = Group.objects.all()[0]
        group.delete()

        self.assertEqual(models.GroupC5Group.objects.all().count(), 0)
        self.assertEqual(models.C5Group.objects.all().count(), 1)

    def test_add_user(self):
        import wingdbstub

        self.test_add_new_group()

        group = Group.objects.all()[0]

        user1 = Database.new_user()
        user2 = Database.new_user()

        user1.groups.add(group)
        user2.groups.add(group)

        self.assertEqual(2, models.C5User.objects.all().count())

    #def test_remove_user(self):
        #self.test_add_user()

#class Concrete5MultipleInstancesTestCase(Concrete5BaseTestCase):
    #def setUp(self):
        #self.init_database('test_c53')
        #self.init_database('test_c52')

    #def tearDown(self):
        #self.destroy_database('test_c53')
        #self.destroy_database('test_c52')

    #def test_add_user(self):
        #group = Group.objects.create(name='test group')

        #self.assertEqual(models.GroupsMapper.objects.all().count(), 2)

        #user1 = Database.new_user()
        #user2 = Database.new_user()

        #user1.groups.add(group)
        #user2.groups.add(group)

        #def check_database(database_id):
            #session = nativemodels.get_session(database_id)

            #native_group = nativemodels.NativeGroups.get(session, group.id)
            #native_user1 = nativemodels.NativeUsers.get_by_username(session, user1.username)
            #native_user2 = nativemodels.NativeUsers.get_by_username(session, user2.username)

            #native_ug1 = nativemodels.NativeUserGroups.get(session, native_user1.id, native_group.id)
            #native_ug2 = nativemodels.NativeUserGroups.get(session, native_user2.id, native_group.id)

            #self.assertEqual(native_ug1.uID, native_user1.id)
            #self.assertEqual(native_ug2.gID, group.id)

        #check_database('test_c53')
        #check_database('test_c52')



